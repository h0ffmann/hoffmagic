from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional, List

from hoffmagic.db.engine import get_session
from hoffmagic.services.essays import EssaysService
from hoffmagic.api.schemas import PostRead, PostDetailRead, EssaysResponse

import logging

logger = logging.getLogger("hoffmagic.api.essays")
router = APIRouter()

@router.get("", response_model=EssaysResponse)
async def get_essays(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    tag: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_session)
):
    essays_service = EssaysService(db)
    try:
        # Note: The service method name changed in the diff
        essays_data = await essays_service.get_essays(
            page=page,
            page_size=page_size,
            tag_slug=tag, # Pass tag as tag_slug
            search=search
        )
        return essays_data
    except Exception as e:
        logger.error(f"Error getting essays: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{slug}", response_model=PostDetailRead)
async def get_essay(
    slug: str,
    db: AsyncSession = Depends(get_session)
):
    essays_service = EssaysService(db)
    essay = await essays_service.get_essay_by_slug(slug)
    if not essay:
        raise HTTPException(status_code=404, detail="Essay not found")
    return essay
