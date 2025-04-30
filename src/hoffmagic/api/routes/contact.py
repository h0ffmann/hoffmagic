"""
API routes for the contact functionality.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from hoffmagic.api.schemas import (
    ContactMessageCreate, ContactMessageRead, 
    ContactMessagesResponse, SubscriberCreate, 
    SubscriberRead
)
from hoffmagic.db.engine import get_session
from hoffmagic.services.contact import ContactService

# Initialize logger
logger = logging.getLogger("hoffmagic.api.contact")

# Create router
router = APIRouter()


@router.post(
    "/message",
    response_model=ContactMessageRead,
    status_code=status.HTTP_201_CREATED,
    summary="Send contact message",
    description="Send a contact message through the form",
)
async def send_contact_message(
    message: ContactMessageCreate,
    db: AsyncSession = Depends(get_session),
):
    """
    Send a contact message through the form.
    """
    try:
        contact_service = ContactService(db)
        return await contact_service.create_message(message)
    except Exception as e:
        logger.error(f"Error sending contact message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send contact message",
        )


@router.get(
    "/messages",
    response_model=ContactMessagesResponse,
    summary="List contact messages",
    description="Get a paginated list of contact messages (admin only)",
)
async def list_contact_messages(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_session),
):
    """
    Get a paginated list of contact messages (admin only).
    """
    try:
        contact_service = ContactService(db)
        return await contact_service.list_messages(page=page, page_size=page_size)
    except Exception as e:
        logger.error(f"Error listing contact messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve contact messages",
        )


@router.post(
    "/subscribe",
    response_model=SubscriberRead,
    status_code=status.HTTP_201_CREATED,
    summary="Subscribe to newsletter",
    description="Subscribe to the blog newsletter",
)
async def subscribe_to_newsletter(
    subscriber: SubscriberCreate,
    db: AsyncSession = Depends(get_session),
):
    """
    Subscribe to the blog newsletter.
    """
    try:
        contact_service = ContactService(db)
        return await contact_service.create_subscriber(subscriber)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subscribing to newsletter: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to subscribe to newsletter",
        )


@router.post(
    "/unsubscribe/{email}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unsubscribe from newsletter",
    description="Unsubscribe from the blog newsletter",
)
async def unsubscribe_from_newsletter(
    email: str = Path(..., description="Subscriber email"),
    db: AsyncSession = Depends(get_session),
):
    """
    Unsubscribe from the blog newsletter.
    """
    try:
        contact_service = ContactService(db)
        success = await contact_service.unsubscribe(email)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscriber with email '{email}' not found",
            )
            
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unsubscribing from newsletter: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unsubscribe from newsletter",
        )
