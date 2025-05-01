# src/hoffmagic/cli_tools/seed_content.py

import asyncio
import datetime
import logging
import sys
from pathlib import Path
from typing import List, Optional

import frontmatter
import typer
from slugify import slugify
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# --- Add Project Root (Keep this) ---
project_root = Path(__file__).resolve().parent.parent.parent.parent
src_path = project_root / 'src'
if not src_path.is_dir():
    print(f"Warning: Could not automatically determine project root containing 'src'. Calculated root: {project_root}", file=sys.stderr)
else:
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        print(f"Added project root to sys.path: {project_root}", file=sys.stderr)


try:
    from src.hoffmagic.config import settings
    from src.hoffmagic.db.engine import SessionLocal
    from src.hoffmagic.db.models import Author, Post, Tag
except ImportError as e:
    print(f"Error importing application modules AFTER adding sys.path: {e}", file=sys.stderr)
    sys.exit(1)

# Configure logging
log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__name__)

app = typer.Typer()

# --- Helper Functions (remain async) ---

async def get_author_by_name(db: AsyncSession, name: str) -> Optional[Author]:
    # (Keep this function as is)
    logger.debug(f"Looking for author with name: {name}")
    result = await db.execute(select(Author).filter_by(name=name))
    author = result.scalar_one_or_none()
    if not author:
        logger.warning(f"Author '{name}' not found in the database.")
    return author

async def get_or_create_tags(db: AsyncSession, tag_names: List[str]) -> List[Tag]:
    # (Keep this function as is)
    if not tag_names:
        return []
    tags_to_return: List[Tag] = []
    tag_slugs = [slugify(name) for name in tag_names]
    existing_tags_result = await db.execute(
        select(Tag).filter(Tag.slug.in_(tag_slugs))
    )
    existing_tags_map = {tag.slug: tag for tag in existing_tags_result.scalars().all()}
    logger.debug(f"Found existing tags: {list(existing_tags_map.keys())}")
    for name, slug in zip(tag_names, tag_slugs):
        if slug in existing_tags_map:
            tags_to_return.append(existing_tags_map[slug])
        else:
            logger.info(f"Creating new tag: '{name}' (slug: {slug})")
            new_tag = Tag(name=name, slug=slug)
            db.add(new_tag)
            try:
                await db.flush()
                await db.refresh(new_tag)
                tags_to_return.append(new_tag)
                existing_tags_map[slug] = new_tag
                logger.debug(f"Added new tag '{name}' to session.")
            except IntegrityError:
                await db.rollback()
                existing_tag = await db.scalar(select(Tag).filter_by(slug=slug))
                if existing_tag:
                    tags_to_return.append(existing_tag)
                else:
                    logger.error(f"Could not create or find tag {name}. Skipping tag.")
            except Exception as e:
                await db.rollback()
                logger.error(f"Unexpected error creating tag '{name}': {e}")
    return tags_to_return


# --- NEW Internal Async Logic Function ---
async def _seed_logic(directory: Path, is_essay: bool, overwrite: bool, dry_run: bool):
    """Contains the core async logic for seeding."""
    typer.echo(f"Scanning directory: {directory}")
    if dry_run:
        typer.secho("--- DRY RUN MODE ENABLED ---", fg=typer.colors.YELLOW)

    markdown_files = list(directory.glob("*.md"))
    if not markdown_files:
        typer.secho(f"No markdown files found in {directory}", fg=typer.colors.RED)
        return

    typer.echo(f"Found {len(markdown_files)} markdown files.")

    processed_count = 0
    skipped_count = 0
    created_count = 0
    updated_count = 0
    error_count = 0

    async with SessionLocal() as db:
        for md_file in markdown_files:
            action = "" # Reset action for each file
            try:
                typer.echo(f"\n--- Processing: {md_file.name} ---")
                parsed_md = frontmatter.load(md_file)
                metadata = parsed_md.metadata
                content = parsed_md.content

                # --- Validate required metadata ---
                required_fields = ["title", "slug", "author"]
                missing_fields = [f for f in required_fields if f not in metadata]
                if missing_fields:
                    logger.error(f"Skipping {md_file.name}: Missing required frontmatter fields: {missing_fields}")
                    skipped_count += 1
                    continue

                # --- Extract metadata ---
                title = str(metadata.get("title"))
                slug = str(metadata.get("slug"))
                author_name = str(metadata.get("author"))
                summary = metadata.get("summary", None)
                summary = str(summary) if summary is not None else None
                is_published = bool(metadata.get("published", False))
                tag_names = metadata.get("tags", [])
                featured_image = metadata.get("featured_image", None)
                publish_date_str = metadata.get("publish_date", None)

                # --- Sanitize/Process metadata ---
                if isinstance(tag_names, list) and all(isinstance(t, str) for t in tag_names):
                     pass
                elif isinstance(tag_names, str):
                     tag_names = [t.strip() for t in tag_names.split(',') if t.strip()]
                     logger.warning(f"Parsed tags from string for {md_file.name}. Recommended format is a YAML list.")
                else:
                    logger.warning(f"Invalid format for tags in {md_file.name}. Should be a list of strings. Skipping tags.")
                    tag_names = []

                author = await get_author_by_name(db, author_name)
                if not author:
                    logger.error(f"Skipping {md_file.name}: Author '{author_name}' not found.")
                    skipped_count += 1
                    continue

                tags = await get_or_create_tags(db, tag_names)

                publish_date = None
                if publish_date_str:
                    try:
                        publish_date = datetime.datetime.fromisoformat(str(publish_date_str))
                        if publish_date.tzinfo is None:
                             publish_date = publish_date.replace(tzinfo=datetime.timezone.utc)
                    except ValueError:
                        logger.warning(f"Could not parse publish_date '{publish_date_str}' in {md_file.name}. Setting publish_date to None.")

                if not publish_date and is_published:
                     publish_date = datetime.datetime.now(datetime.timezone.utc)
                     logger.info(f"No publish_date found for published post {md_file.name}. Setting to current time.")

                # --- Check if post exists ---
                existing_post_stmt = (
                    select(Post)
                    .where(Post.slug == slug)
                    .options(selectinload(Post.tags))
                )
                existing_post = (await db.execute(existing_post_stmt)).scalar_one_or_none()

                post_data_dict = {
                    "title": title, "content": content, "summary": summary,
                    "is_published": is_published, "is_essay": is_essay,
                    "author_id": author.id, "publish_date": publish_date,
                    "featured_image": str(featured_image) if featured_image else None
                }

                # --- Perform Create or Update ---
                if existing_post:
                    logger.info(f"Post with slug '{slug}' already exists.")
                    if overwrite:
                        logger.warning(f"--overwrite enabled. Updating post: {slug}")
                        for key, value in post_data_dict.items():
                            setattr(existing_post, key, value)
                        existing_post.tags = tags
                        action = "Updated"
                        updated_count += 1
                    else:
                        logger.info(f"Skipping existing post {slug} (use --overwrite to update).")
                        skipped_count += 1
                        continue
                else:
                    logger.info(f"Creating new post: {slug}")
                    new_post = Post(slug=slug, **post_data_dict)
                    new_post.tags = tags
                    db.add(new_post)
                    action = "Created"
                    created_count += 1

                # --- Commit or Dry Run ---
                if dry_run:
                    logger.info(f"[Dry Run] Would have {action.lower()} post '{title}' (slug: {slug})")
                    # Need to rollback tags potentially flushed during get_or_create_tags
                    await db.rollback()
                elif action: # Only commit if action was taken
                    try:
                        await db.commit()
                        logger.info(f"Successfully {action.lower()} post '{title}' (slug: {slug})")
                        processed_count += 1
                    except IntegrityError as e:
                        await db.rollback()
                        logger.error(f"Database error committing {md_file.name} (slug: {slug}): {e}")
                        error_count += 1
                    except Exception as e:
                        await db.rollback()
                        logger.error(f"Unexpected error committing post {md_file.name} (slug: {slug}): {e}")
                        error_count += 1
                # No 'else' needed here, handled by 'continue' or action being set

            except frontmatter.exceptions.FrontmatterError as e:
                logger.error(f"Error parsing frontmatter in {md_file.name}: {e}")
                error_count += 1
                await db.rollback()
            except Exception as e:
                logger.error(f"Unexpected error processing file {md_file.name}: {e}", exc_info=True)
                error_count += 1
                await db.rollback()

        # Final Summary
        typer.secho("\n--- Processing Complete ---", fg=typer.colors.GREEN)
        typer.echo(f"Total files found: {len(markdown_files)}")
        if not dry_run:
            typer.echo(f"Posts created: {created_count}")
            typer.echo(f"Posts updated: {updated_count}")
        typer.echo(f"Files skipped (missing fields, author not found, or exists without overwrite): {skipped_count}")
        typer.echo(f"Files with errors: {error_count}")
        if dry_run:
            typer.secho("--- DRY RUN MODE: No changes were saved to the database ---", fg=typer.colors.YELLOW)


# --- Main Typer Command (NOW SYNCHRONOUS) ---
@app.command()
def seed( # REMOVED async
    directory: Path = typer.Argument(
        ..., # Make directory path mandatory
        exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True,
        help="Path to the directory containing Markdown files (.md). Example: src/content/blog",
    ),
    is_essay: bool = typer.Option(False, "--essay", help="Mark all processed posts as essays."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing posts found with the same slug."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Scan files and log actions without saving to database.")
):
    """
    Seeds the database with Posts from Markdown files in the specified DIRECTORY.

    Parses files with YAML frontmatter. Requires Author records to exist.
    Tags will be created if they don't exist.
    """
    try:
        # Explicitly run the async logic using asyncio.run
        asyncio.run(_seed_logic(directory, is_essay, overwrite, dry_run))
    except Exception as e:
        logger.error(f"An error occurred during the seeding process: {e}", exc_info=True)
        sys.exit(1) # Exit with error code if async run fails


# --- Entry point for running script ---
if __name__ == "__main__":
    app() # Run the Typer app