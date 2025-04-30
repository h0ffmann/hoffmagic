"""
Service layer for about functionality.
"""
import logging
from typing import Dict, Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from hoffmagic.db.models import Author, Post, Tag, Comment

# Initialize logger
logger = logging.getLogger("hoffmagic.services.about")


class AboutService:
    """
    Service for about page related operations.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize with a database session.
        
        Args:
            db: SQLAlchemy async session
        """
        self.db = db
    
    async def get_author_info(self) -> Optional[Author]:
        """
        Get the primary author information.
        
        Returns:
            Author object if found, None otherwise
        """
        # Get the first author (for simplicity)
        query = select(Author).order_by(Author.id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_author_info(self, author_data: Dict[str, Any]) -> Optional[Author]:
        """
        Update the author information.
        
        Args:
            author_data: Author data dictionary
            
        Returns:
            Updated author object if found, None otherwise
        """
        # Get the first author
        author = await self.get_author_info()
        
        if not author:
            return None
        
        # Update author fields
        for key, value in author_data.model_dump(exclude_unset=True).items():
            setattr(author, key, value)
        
        # Save changes
        await self.db.commit()
        await self.db.refresh(author)
        
        return author
    
    async def get_blog_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the blog.
        
        Returns:
            Dictionary with blog statistics
        """
        # Count posts
        post_count_query = select(func.count()).select_from(
            select(Post).where(and_(Post.is_published == True, Post.is_essay == False)).subquery()
        )
        post_count = await self.db.scalar(post_count_query) or 0
        
        # Count essays
        essay_count_query = select(func.count()).select_from(
            select(Post).where(and_(Post.is_published == True, Post.is_essay == True)).subquery()
        )
        essay_count = await self.db.scalar(essay_count_query) or 0
        
        # Count tags
        tag_count_query = select(func.count()).select_from(Tag)
        tag_count = await self.db.scalar(tag_count_query) or 0
        
        # Count comments
        comment_count_query = select(func.count()).select_from(
            select(Comment).where(Comment.is_approved == True).subquery()
        )
        comment_count = await self.db.scalar(comment_count_query) or 0
        
        return {
            "post_count": post_count,
            "essay_count": essay_count,
            "tag_count": tag_count,
            "comment_count": comment_count,
        }
