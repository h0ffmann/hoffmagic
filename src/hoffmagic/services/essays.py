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
from sqlalchemy import select, func, or_, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.future import select # Keep if used elsewhere or consolidate

from hoffmagic.config import settings
from hoffmagic.db.models import Post, Author, Tag, Comment, post_tags # Ensure Comment is imported if needed
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

    # --- Helper function (optional, remove if not used elsewhere) ---
    # def _get_localized_field(self, obj, field_name: str, lang: str) -> Any:
    #     if lang == "pt":
    #         pt_field_name = f"{field_name}_pt"
    #         localized_value = getattr(obj, pt_field_name, None)
    #         if localized_value:
    #             return localized_value
    #     return getattr(obj, field_name, None)

    async def get_essays(
        self,
        page: int = 1,
        page_size: int = 10,
        tag_slug: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get essays with pagination, filtering, and search.
        """
        try:
            query = (
                select(Post)
                .where(Post.is_published == True)
                .where(Post.is_essay == True)
                .options(
                    selectinload(Post.author),
                    selectinload(Post.tags)
                )
                .order_by(desc(Post.publish_date))
            )

            # Apply tag filter
            if tag_slug:
                tag_subquery = select(Tag.id).where(Tag.slug == tag_slug).scalar_subquery()
                query = query.join(post_tags).where(post_tags.c.tag_id == tag_subquery)

            # Apply search filter
            if search:
                search_term = f"%{search}%"
                query = query.where(
                    or_(
                        Post.title.ilike(search_term),
                        Post.content.ilike(search_term),
                        Post.summary.ilike(search_term)
                    )
                )

            # Get total count for pagination
            count_query = select(func.count()).select_from(query.subquery())
            total = await self.db.scalar(count_query) or 0

            # Apply pagination
            query = query.offset((page - 1) * page_size).limit(page_size)
            essays = (await self.db.execute(query)).scalars().all()

            # Calculate pages
            pages = (total + page_size - 1) // page_size if total > 0 else 1

            return {
                "items": essays,
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": pages
            }
        except Exception as e:
            logger.error(f"Error getting essays: {str(e)}")
            raise

    async def get_essay_by_slug(self, slug: str, lang: str = 'en') -> Optional[Post]:
        """
        Get an essay by its slug, applying localization if necessary.

        Args:
            slug: Essay slug
            lang: Language code ('en' or 'pt')

        Returns:
            Essay object if found, None otherwise
        """
        logger.debug(f"Fetching essay by slug: {slug}, lang: {lang}")
        # Essays are just posts with is_essay=True
        query = (
            select(Post)
            .where(Post.slug == slug, Post.is_essay == True) # Combined where
            .options(
                selectinload(Post.tags), # Use selectinload for collections
                selectinload(Post.author) # Use selectinload for one-to-one/many-to-one
                # Comments might not be relevant for essays, adjust as needed
                # If needed: selectinload(Post.comments).where(Comment.is_approved == True)
            )
        )
        result = await self.db.execute(query)
        essay = result.scalars().first() # Use scalars().first()

        if essay and lang == 'pt':
            logger.debug(f"Essay found, attempting to localize fields to Portuguese for slug: {slug}")
            # Overwrite fields with Portuguese versions if they exist and are not empty
            title_pt = getattr(essay, 'title_pt', None)
            content_pt = getattr(essay, 'content_pt', None)
            summary_pt = getattr(essay, 'summary_pt', None)

            if title_pt:
                essay.title = title_pt
                logger.debug(f"Applied title_pt for essay slug: {slug}")
            if content_pt:
                essay.content = content_pt
                logger.debug(f"Applied content_pt for essay slug: {slug}")
            if summary_pt:
                essay.summary = summary_pt
                logger.debug(f"Applied summary_pt for essay slug: {slug}")
            # Localize comments if loaded and relevant
            # if essay.comments:
            #      for comment in essay.comments:
            #          if hasattr(comment, 'content_pt') and comment.content_pt:
            #              comment.content = comment.content_pt
            #              logger.debug(f"Applied content_pt for comment ID: {comment.id} on essay slug: {slug}")

        return essay

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
    # Removed load_markdown_essays. Content syncing should be explicit.
