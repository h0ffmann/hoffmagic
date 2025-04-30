"""
API routes for the about me functionality.
"""
import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from hoffmagic.api.schemas import AuthorRead, AuthorUpdate
from hoffmagic.db.engine import get_session
from hoffmagic.services.about import AboutService

# Initialize logger
logger = logging.getLogger("hoffmagic.api.about")

# Create router
router = APIRouter()


@router.get(
    "/",
    response_model=AuthorRead,
    summary="Get author info",
    description="Get the author's information for the About Me page",
)
async def get_author_info(
    db: AsyncSession = Depends(get_session),
):
    """
    Get the author's information for the About Me page.
    """
    try:
        about_service = AboutService(db)
        author = await about_service.get_author_info()
        
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author information not found",
            )
            
        return author
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving author information: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve author information",
        )


@router.put(
    "/",
    response_model=AuthorRead,
    summary="Update author info",
    description="Update the author's information for the About Me page",
)
async def update_author_info(
    author: AuthorUpdate,
    db: AsyncSession = Depends(get_session),
):
    """
    Update the author's information for the About Me page.
    """
    try:
        about_service = AboutService(db)
        updated_author = await about_service.update_author_info(author)
        
        if not updated_author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author information not found",
            )
            
        return updated_author
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating author information: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update author information",
        )


@router.get(
    "/stats",
    response_model=Dict[str, Any],
    summary="Get blog stats",
    description="Get statistics about the blog for the About Me page",
)
async def get_blog_stats(
    db: AsyncSession = Depends(get_session),
):
    """
    Get statistics about the blog for the About Me page.
    """
    try:
        about_service = AboutService(db)
        return await about_service.get_blog_stats()
    except Exception as e:
        logger.error(f"Error retrieving blog statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve blog statistics",
        )
