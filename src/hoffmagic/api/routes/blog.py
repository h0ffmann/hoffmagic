"""
API routes for the blog functionality.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from hoffmagic.api.schemas import (
    PostCreate, PostUpdate, PostRead, PostDetailRead, 
    BlogPostsResponse, CommentCreate, CommentRead
)
from hoffmagic.db.engine import get_session
from hoffmagic.services.blog import BlogService

# Initialize logger
logger = logging.getLogger("hoffmagic.api.blog")

# Create router
router = APIRouter()


@router.get(
    "/", 
    response_model=BlogPostsResponse,
    summary="List blog posts",
    description="Get a paginated list of published blog posts",
)
async def list_posts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    tag: Optional[str] = Query(None, description="Filter by tag slug"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    db: AsyncSession = Depends(get_session),
):
    """
    List published blog posts with pagination, filtering, and search.
    """
    try:
        blog_service = BlogService(db)
        return await blog_service.list_posts(
            page=page,
            page_size=page_size,
            tag=tag,
            search=search,
            is_essay=False,
        )
    except Exception as e:
        logger.error(f"Error listing blog posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve blog posts",
        )


@router.get(
    "/{slug}",
    response_model=PostDetailRead,
    summary="Get blog post",
    description="Get a specific blog post by slug",
)
async def get_post(
    slug: str = Path(..., description="Blog post slug"),
    db: AsyncSession = Depends(get_session),
):
    """
    Get a specific blog post by its slug.
    """
    try:
        blog_service = BlogService(db)
        post = await blog_service.get_post_by_slug(slug, is_essay=False)
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blog post with slug '{slug}' not found",
            )
            
        return post
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving blog post '{slug}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve blog post",
        )


@router.post(
    "/",
    response_model=PostRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create blog post",
    description="Create a new blog post",
)
async def create_post(
    post: PostCreate,
    db: AsyncSession = Depends(get_session),
):
    """
    Create a new blog post.
    """
    try:
        # Ensure it's marked as a blog post, not an essay
        post_data = post.model_dump()
        post_data["is_essay"] = False
        
        blog_service = BlogService(db)
        return await blog_service.create_post(post_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating blog post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create blog post",
        )


@router.put(
    "/{slug}",
    response_model=PostRead,
    summary="Update blog post",
    description="Update an existing blog post",
)
async def update_post(
    slug: str = Path(..., description="Blog post slug"),
    post: PostUpdate = ...,
    db: AsyncSession = Depends(get_session),
):
    """
    Update an existing blog post.
    """
    try:
        blog_service = BlogService(db)
        updated_post = await blog_service.update_post(slug, post, is_essay=False)
        
        if not updated_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blog post with slug '{slug}' not found",
            )
            
        return updated_post
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating blog post '{slug}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update blog post",
        )


@router.delete(
    "/{slug}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete blog post",
    description="Delete an existing blog post",
)
async def delete_post(
    slug: str = Path(..., description="Blog post slug"),
    db: AsyncSession = Depends(get_session),
):
    """
    Delete an existing blog post.
    """
    try:
        blog_service = BlogService(db)
        success = await blog_service.delete_post(slug, is_essay=False)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blog post with slug '{slug}' not found",
            )
            
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting blog post '{slug}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete blog post",
        )


@router.post(
    "/{slug}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add comment",
    description="Add a comment to a blog post",
)
async def add_comment(
    slug: str = Path(..., description="Blog post slug"),
    comment: CommentCreate = ...,
    db: AsyncSession = Depends(get_session),
):
    """
    Add a comment to a blog post.
    """
    try:
        blog_service = BlogService(db)
        return await blog_service.add_comment(slug, comment)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding comment to blog post '{slug}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add comment",
        )
