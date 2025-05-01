from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from hoffmagic.db.engine import get_session  
from hoffmagic.services.contact import ContactService
from hoffmagic.api.schemas import SubscriberCreate, ContactMessageCreate

import logging

logger = logging.getLogger("hoffmagic.api.contact")
router = APIRouter()

@router.post("/subscribe", response_model=Dict[str, Any])
async def subscribe(
    subscriber_data: SubscriberCreate,
    db: AsyncSession = Depends(get_session)
):
    contact_service = ContactService(db)
    try:
        subscriber = await contact_service.create_subscriber(subscriber_data)
        return {"success": True, "message": "Successfully subscribed"}
    except Exception as e:
        logger.error(f"Subscription error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/message", response_model=Dict[str, Any])
async def send_message(
    message_data: ContactMessageCreate,
    db: AsyncSession = Depends(get_session)
):
    contact_service = ContactService(db)
    try:
        message = await contact_service.create_message(message_data)
        return {"success": True, "message": "Message sent successfully"}
    except Exception as e:
        logger.error(f"Message sending error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/unsubscribe/{email}", response_model=Dict[str, Any])
async def unsubscribe(
    email: str,
    db: AsyncSession = Depends(get_session)
):
    contact_service = ContactService(db)
    success = await contact_service.unsubscribe(email)
    if success:
        return {"success": True, "message": "Successfully unsubscribed"}
    else:
        raise HTTPException(status_code=404, detail="Email not found")
