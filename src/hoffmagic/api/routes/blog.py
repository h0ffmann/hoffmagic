from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional, List

from hoffmagic.db.engine import get_session
from hoffmagic.services.blog import BlogService
from hoffmagic.api.schemas import PostRead, PostDetailRead, BlogPostsResponse

import logging

logger = logging.getLogger("hoffmagic.api.blog")
router = APIRouter()

@router.get("", response_model=BlogPostsResponse)
async def get_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    tag: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_session)
):
    blog_service = BlogService(db)
    try:
        # Note: The service method name changed in the diff
        posts_data = await blog_service.get_posts(
            page=page,
            page_size=page_size,
            tag_slug=tag, # Pass tag as tag_slug
            search=search,
            is_essay=False
        )
        return posts_data
    except Exception as e:
        logger.error(f"Error getting posts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{slug}", response_model=PostDetailRead)
async def get_post(
    slug: str,
    db: AsyncSession = Depends(get_session)
):
    blog_service = BlogService(db)
    post = await blog_service.get_post_by_slug(slug, is_essay=False)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
