"""
API routes for the essays functionality.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from hoffmagic.api.schemas import (
    PostCreate, PostUpdate, PostRead, PostDetailRead, 
    EssaysResponse
)
from hoffmagic.db.engine import get_session
from hoffmagic.services.essays import EssaysService

# Initialize logger
logger = logging.getLogger("hoffmagic.api.essays")

# Create router
router = APIRouter()


@router.get(
    "/", 
    response_model=EssaysResponse,
    summary="List essays",
    description="Get a paginated list of published essays",
)
async def list_essays(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    tag: Optional[str] = Query(None, description="Filter by tag slug"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    db: AsyncSession = Depends(get_session),
):
    """
    List published essays with pagination, filtering, and search.
    """
    try:
        essays_service = EssaysService(db)
        return await essays_service.list_essays(
            page=page,
            page_size=page_size,
            tag=tag,
            search=search,
        )
    except Exception as e:
        logger.error(f"Error listing essays: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve essays",
        )


@router.get(
    "/{slug}",
    response_model=PostDetailRead,
    summary="Get essay",
    description="Get a specific essay by slug",
)
async def get_essay(
    slug: str = Path(..., description="Essay slug"),
    db: AsyncSession = Depends(get_session),
):
    """
    Get a specific essay by its slug.
    """
    try:
        essays_service = EssaysService(db)
        essay = await essays_service.get_essay_by_slug(slug)
        
        if not essay:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Essay with slug '{slug}' not found",
            )
            
        return essay
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving essay '{slug}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve essay",
        )


@router.post(
    "/",
    response_model=PostRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create essay",
    description="Create a new essay",
)
async def create_essay(
    essay: PostCreate,
    db: AsyncSession = Depends(get_session),
):
    """
    Create a new essay.
    """
    try:
        # Ensure it's marked as an essay, not a blog post
        essay_data = essay.model_dump()
        essay_data["is_essay"] = True
        
        essays_service = EssaysService(db)
        return await essays_service.create_essay(essay_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating essay: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create essay",
        )


@router.put(
    "/{slug}",
    response_model=PostRead,
    summary="Update essay",
    description="Update an existing essay",
)
async def update_essay(
    slug: str = Path(..., description="Essay slug"),
    essay: PostUpdate = ...,
    db: AsyncSession = Depends(get_session),
):
    """
    Update an existing essay.
    """
    try:
        essays_service = EssaysService(db)
        updated_essay = await essays_service.update_essay(slug, essay)
        
        if not updated_essay:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Essay with slug '{slug}' not found",
            )
            
        return updated_essay
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating essay '{slug}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update essay",
        )


@router.delete(
    "/{slug}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete essay",
    description="Delete an existing essay",
)
async def delete_essay(
    slug: str = Path(..., description="Essay slug"),
    db: AsyncSession = Depends(get_session),
):
    """
    Delete an existing essay.
    """
    try:
        essays_service = EssaysService(db)
        success = await essays_service.delete_essay(slug)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Essay with slug '{slug}' not found",
            )
            
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting essay '{slug}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete essay",
        )
