"""
Service layer for essays functionality.
"""
import os
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import frontmatter
import markdown
from fastapi import HTTPException, status
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from hoffmagic.config import settings
from hoffmagic.db.models import Post, Author, Tag
from hoffmagic.api.schemas import (
    PostCreate, PostUpdate, EssaysResponse
)

# Initialize logger
logger = logging.getLogger("hoffmagic.services.essays")


class EssaysService:
    """
    Service for essays-related operations.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize with a database session.
        
        Args:
            db: SQLAlchemy async session
        """
        self.db = db
    
    async def list_essays(
        self, 
        page: int = 1, 
        page_size: int = 10,
        tag: Optional[str] = None,
        search: Optional[str] = None,
    ) -> EssaysResponse:
        """
        List essays with pagination, filtering, and search.
        
        Args:
            page: Page number
            page_size: Items per page
            tag: Filter by tag slug
            search: Search in title and content
            
        Returns:
            Paginated response with essays
        """
        # Base query for published essays
        query = (
            select(Post)
            .where(and_(Post.is_published == True, Post.is_essay == True))
            .order_by(Post.publish_date.desc())
            .options(
                joinedload(Post.author),
                joinedload(Post.tags)
            )
        )
        
        # Apply tag filter if provided
        if tag:
            query = (
                query
                .join(Post.tags)
                .where(Tag.slug == tag)
            )
        
        # Apply search filter if provided
        if search:
            search_term = f"%{search}%"
            query = (
                query
                .where(
                    or_(
                        Post.title.ilike(search_term),
                        Post.content.ilike(search_term),
                        Post.summary.ilike(search_term),
                    )
                )
            )
        
        # Count total items
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0
        
        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        essays = (await self.db.execute(query)).scalars().all()
        
        # Calculate total pages
        pages = (total + page_size - 1) // page_size
        
        return {
            "items": essays,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        }
    
    async def get_essay_by_slug(self, slug: str) -> Optional[Post]:
        """
        Get an essay by its slug.
        
        Args:
            slug: Essay slug
            
        Returns:
            Essay object if found, None otherwise
        """
        query = (
            select(Post)
            .where(and_(Post.slug == slug, Post.is_essay == True))
            .options(
                joinedload(Post.author),
                joinedload(Post.tags),
                joinedload(Post.comments)
            )
        )
        
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def create_essay(self, essay_data: Dict[str, Any]) -> Post:
        """
        Create a new essay.
        
        Args:
            essay_data: Essay data dictionary
            
        Returns:
            Created essay object
        """
        # Check if slug is already in use
        existing_essay = await self.get_essay_by_slug(essay_data["slug"])
        if existing_essay:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Essay with slug '{essay_data['slug']}' already exists",
            )
        
        # Handle tags
        tag_ids = essay_data.pop("tag_ids", [])
        tags = []
        
        if tag_ids:
            query = select(Tag).where(Tag.id.in_(tag_ids))
            result = await self.db.execute(query)
            tags = result.scalars().all()
        
        # Create essay instance
        essay = Post(**essay_data)
        essay.tags = tags
        
        # Add publish date if essay is published
        if essay.is_published:
            essay.publish_date = datetime.now()
        
        # Save to database
        self.db.add(essay)
        await self.db.commit()
        await self.db.refresh(essay)
        
        return essay
    
    async def update_essay(
        self, 
        slug: str, 
        essay_update: PostUpdate,
    ) -> Optional[Post]:
        """
        Update an existing essay.
        
        Args:
            slug: Essay slug
            essay_update: Update data
            
        Returns:
            Updated essay object if found, None otherwise
        """
        # Get existing essay
        essay = await self.get_essay_by_slug(slug)
        
        if not essay:
            return None
        
        # Update essay fields
        update_data = essay_update.model_dump(exclude_unset=True)
        
        # Handle slug change
        new_slug = update_data.get("slug")
        if new_slug and new_slug != slug:
            # Check if new slug is already in use
            existing_essay = await self.get_essay_by_slug(new_slug)
            if existing_essay:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Essay with slug '{new_slug}' already exists",
                )
        
        # Handle tags
        tag_ids = update_data.pop("tag_ids", None)
        if tag_ids is not None:
            query = select(Tag).where(Tag.id.in_(tag_ids))
            result = await self.db.execute(query)
            essay.tags = result.scalars().all()
        
        # Handle publish status change
        if "is_published" in update_data and update_data["is_published"] and not essay.publish_date:
            essay.publish_date = datetime.now()
        
        # Update other fields
        for key, value in update_data.items():
            setattr(essay, key, value)
        
        # Save changes
        await self.db.commit()
        await self.db.refresh(essay)
        
        return essay
    
    async def delete_essay(self, slug: str) -> bool:
        """
        Delete an essay.
        
        Args:
            slug: Essay slug
            
        Returns:
            True if deleted, False if not found
        """
        # Get existing essay
        essay = await self.get_essay_by_slug(slug)
        
        if not essay:
            return False
        
        # Delete essay
        await self.db.delete(essay)
        await self.db.commit()
        
        return True
    
    async def load_markdown_essays(self) -> Tuple[int, int]:
        """
        Load essays from Markdown files.
        
        Returns:
            Tuple of (new essays count, updated essays count)
        """
        new_count = 0
        updated_count = 0
        
        # Get the essays directory
        essays_dir = settings.ESSAYS_DIR
        
        if not os.path.exists(essays_dir):
            logger.warning(f"Essays directory not found: {essays_dir}")
            return new_count, updated_count
        
        # Process each markdown file
        for filename in os.listdir(essays_dir):
            if not filename.endswith('.md'):
                continue
            
            file_path = os.path.join(essays_dir, filename)
            
            try:
                # Parse frontmatter and content
                with open(file_path, 'r', encoding='utf-8') as f:
                    essay_data = frontmatter.load(f)
                
                # Extract metadata
                metadata = essay_data.metadata
                slug = metadata.get('slug') or filename[:-3]
                
                # Required fields
                if not metadata.get('title'):
                    logger.warning(f"Skipping {filename}: Missing title")
                    continue
                
                # Check if essay already exists
                existing_essay = await self.get_essay_by_slug(slug)
                
                # Get or create author
                author_name = metadata.get('author', 'Admin')
                author_query = select(Author).where(Author.name == author_name)
                author = (await self.db.execute(author_query)).scalar_one_or_none()
                
                if not author:
                    author = Author(
                        name=author_name,
                        email=f"{author_name.lower().replace(' ', '.')}@example.com",
                    )
                    self.db.add(author)
                    await self.db.commit()
                
                # Get or create tags
                tags = []
                tag_names = metadata.get('tags', [])
                
                if tag_names:
                    for tag_name in tag_names:
                        tag_slug = tag_name.lower().replace(' ', '-')
                        tag_query = select(Tag).where(Tag.slug == tag_slug)
                        tag = (await self.db.execute(tag_query)).scalar_one_or_none()
                        
                        if not tag:
                            tag = Tag(name=tag_name, slug=tag_slug)
                            self.db.add(tag)
                            await self.db.commit()
                        
                        tags.append(tag)
                
                # Convert markdown to HTML
                content_html = markdown.markdown(
                    essay_data.content,
                    extensions=['fenced_code', 'codehilite', 'tables', 'toc']
                )
                
                # Create or update essay
                essay_data = {
                    'title': metadata.get('title'),
                    'slug': slug,
                    'content': content_html,
                    'summary': metadata.get('summary'),
                    'is_published': metadata.get('published', True),
                    'is_essay': True,
                    'featured_image': metadata.get('featured_image'),
                    'author_id': author.id,
                }
                
                if existing_essay:
                    # Update existing essay
                    for key, value in essay_data.items():
                        setattr(existing_essay, key, value)
                    
                    existing_essay.tags = tags
                    await self.db.commit()
                    updated_count += 1
                else:
                    # Create new essay
                    new_essay = Post(**essay_data)
                    new_essay.tags = tags
                    
                    if new_essay.is_published:
                        new_essay.publish_date = datetime.now()
                    
                    self.db.add(new_essay)
                    await self.db.commit()
                    new_count += 1
                
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")
        
        return new_count, updated_count
