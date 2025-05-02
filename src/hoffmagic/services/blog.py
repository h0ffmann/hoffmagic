"""
Service layer for blog functionality.
"""
import os
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import frontmatter
import markdown
from fastapi import HTTPException, status
from sqlalchemy import select, func, or_, and_, desc # Add desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload # Add selectinload

from hoffmagic.config import settings
from hoffmagic.db.models import Post, Author, Tag, Comment, post_tags # Add post_tags
from hoffmagic.api.schemas import (
    PostCreate, PostUpdate, CommentCreate,
    BlogPostsResponse
)

# Initialize logger
logger = logging.getLogger("hoffmagic.services.blog")


class BlogService:
    """
    Service for blog-related operations.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize with a database session.
        
        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    def _get_localized_field(self, obj, field_name, lang):
        """Get the appropriate field value based on language."""
        if lang == 'pt':
            pt_field = getattr(obj, f"{field_name}_pt", None)
            if pt_field:
                return pt_field
        return getattr(obj, field_name)

    async def get_posts(
        self,
        page: int = 1,
        page_size: int = 10,
        tag_slug: Optional[str] = None,
        search: Optional[str] = None,
        is_essay: bool = False,
        lang: str = 'en'
    ) -> Dict[str, Any]:
        """
        Get posts (or essays) with pagination, filtering, and search.
        """
        try:
            query = (
                select(Post)
                .where(Post.is_published == True)
                .where(Post.is_essay == is_essay)
                .options(
                    selectinload(Post.author),
                    selectinload(Post.tags),
                    # selectinload(Post.comments) # Avoid loading comments in list view
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
            posts = (await self.db.execute(query)).scalars().all()

            # Calculate pages
            pages = (total + page_size - 1) // page_size if total > 0 else 1

            # Localize content before returning
            for post in posts:
                if lang == 'pt':
                    if hasattr(post, 'title_pt') and post.title_pt:
                        post.title = post.title_pt
                    if hasattr(post, 'content_pt') and post.content_pt:
                        post.content = post.content_pt
                    if hasattr(post, 'summary_pt') and post.summary_pt:
                        post.summary = post.summary_pt
                    # Ensure comments are localized too if they exist
                    if post.comments and hasattr(post.comments[0], 'content_pt'):
                        for comment in post.comments:
                            if comment.content_pt:
                                comment.content = comment.content_pt
            
            return {
                "items": posts,
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": pages
            }
        except Exception as e:
            logger.error(f"Error getting posts: {str(e)}")
            raise

    async def get_post_by_slug(
        self, 
        slug: str,
        is_essay: bool = False,
    ) -> Optional[Post]:
        """
        Get a post by its slug.
        
        Args:
            slug: Post slug
            is_essay: Whether the post is an essay
            
        Returns:
            Post object if found, None otherwise
        """
        query = (
            select(Post)
            .where(and_(Post.slug == slug, Post.is_essay == is_essay))
            .options(
                joinedload(Post.author),
                joinedload(Post.tags),
                joinedload(Post.comments)
            )
        )
        
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def create_post(self, post_data: Dict[str, Any]) -> Post:
        """
        Create a new blog post.
        
        Args:
            post_data: Post data dictionary
            
        Returns:
            Created post object
        """
        # Check if slug is already in use
        existing_post = await self.get_post_by_slug(post_data["slug"])
        if existing_post:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Post with slug '{post_data['slug']}' already exists",
            )
        
        # Handle tags
        tag_ids = post_data.pop("tag_ids", [])
        tags = []
        
        if tag_ids:
            query = select(Tag).where(Tag.id.in_(tag_ids))
            result = await self.db.execute(query)
            tags = result.scalars().all()
        
        # Create post instance
        post = Post(**post_data)
        post.tags = tags
        
        # Add publish date if post is published
        if post.is_published:
            post.publish_date = datetime.now()
        
        # Save to database
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        
        return post
    
    async def update_post(
        self, 
        slug: str, 
        post_update: PostUpdate,
        is_essay: bool = False,
    ) -> Optional[Post]:
        """
        Update an existing blog post.
        
        Args:
            slug: Post slug
            post_update: Update data
            is_essay: Whether the post is an essay
            
        Returns:
            Updated post object if found, None otherwise
        """
        # Get existing post
        post = await self.get_post_by_slug(slug, is_essay)
        
        if not post:
            return None
        
        # Update post fields
        update_data = post_update.model_dump(exclude_unset=True)
        
        # Handle slug change
        new_slug = update_data.get("slug")
        if new_slug and new_slug != slug:
            # Check if new slug is already in use
            existing_post = await self.get_post_by_slug(new_slug, is_essay)
            if existing_post:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Post with slug '{new_slug}' already exists",
                )
        
        # Handle tags
        tag_ids = update_data.pop("tag_ids", None)
        if tag_ids is not None:
            query = select(Tag).where(Tag.id.in_(tag_ids))
            result = await self.db.execute(query)
            post.tags = result.scalars().all()
        
        # Handle publish status change
        if "is_published" in update_data and update_data["is_published"] and not post.publish_date:
            post.publish_date = datetime.now()
        
        # Update other fields
        for key, value in update_data.items():
            setattr(post, key, value)
        
        # Save changes
        await self.db.commit()
        await self.db.refresh(post)
        
        return post
    
    async def delete_post(
        self, 
        slug: str,
        is_essay: bool = False,
    ) -> bool:
        """
        Delete a blog post.
        
        Args:
            slug: Post slug
            is_essay: Whether the post is an essay
            
        Returns:
            True if deleted, False if not found
        """
        # Get existing post
        post = await self.get_post_by_slug(slug, is_essay)
        
        if not post:
            return False
        
        # Delete post
        await self.db.delete(post)
        await self.db.commit()
        
        return True
    
    async def add_comment(
        self, 
        slug: str, 
        comment_data: CommentCreate,
    ) -> Comment:
        """
        Add a comment to a blog post.
        
        Args:
            slug: Post slug
            comment_data: Comment data
            
        Returns:
            Created comment object
        """
        # Get the post
        post = await self.get_post_by_slug(slug)
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with slug '{slug}' not found",
            )
        
        # Create comment
        comment = Comment(
            content=comment_data.content,
            author_name=comment_data.author_name,
            author_email=comment_data.author_email,
            post_id=post.id,
            parent_id=comment_data.parent_id,
            is_approved=False,  # Comments require approval by default
        )
        
        # Save to database
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        
        return comment
    # Removed load_markdown_posts. Content syncing should be explicit.
