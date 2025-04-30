"""
Service layer for contact functionality.
"""
import logging
from typing import Dict, Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from hoffmagic.db.models import ContactMessage, Subscriber
from hoffmagic.api.schemas import (
    ContactMessageCreate, SubscriberCreate, 
    ContactMessagesResponse
)

# Initialize logger
logger = logging.getLogger("hoffmagic.services.contact")


class ContactService:
    """
    Service for contact page related operations.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize with a database session.
        
        Args:
            db: SQLAlchemy async session
        """
        self.db = db
    
    async def create_message(self, message_data: ContactMessageCreate) -> ContactMessage:
        """
        Create a new contact message.
        
        Args:
            message_data: Contact message data
            
        Returns:
            Created contact message object
        """
        # Create message instance
        message = ContactMessage(**message_data.model_dump())
        
        # Save to database
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        
        return message
    
    async def list_messages(
        self, 
        page: int = 1, 
        page_size: int = 20,
    ) -> ContactMessagesResponse:
        """
        List contact messages with pagination.
        
        Args:
            page: Page number
            page_size: Items per page
            
        Returns:
            Paginated response with contact messages
        """
        # Base query for contact messages
        query = (
            select(ContactMessage)
            .order_by(ContactMessage.created_at.desc())
        )
        
        # Count total items
        count_query = select(func.count()).select_from(ContactMessage)
        total = await self.db.scalar(count_query) or 0
        
        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        messages = (await self.db.execute(query)).scalars().all()
        
        # Calculate total pages
        pages = (total + page_size - 1) // page_size
        
        return {
            "items": messages,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        }
    
    async def create_subscriber(self, subscriber_data: SubscriberCreate) -> Subscriber:
        """
        Create a new newsletter subscriber.
        
        Args:
            subscriber_data: Subscriber data
            
        Returns:
            Created subscriber object
        """
        # Check if email already subscribed
        query = select(Subscriber).where(Subscriber.email == subscriber_data.email)
        existing_subscriber = (await self.db.execute(query)).scalar_one_or_none()
        
        if existing_subscriber:
            if existing_subscriber.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already subscribed",
                )
            else:
                # Reactivate subscription
                existing_subscriber.is_active = True
                await self.db.commit()
                await self.db.refresh(existing_subscriber)
                return existing_subscriber
        
        # Create subscriber instance
        subscriber = Subscriber(**subscriber_data.model_dump())
        
        # Save to database
        self.db.add(subscriber)
        await self.db.commit()
        await self.db.refresh(subscriber)
        
        return subscriber
    
    async def unsubscribe(self, email: str) -> bool:
        """
        Unsubscribe from newsletter.
        
        Args:
            email: Subscriber email
            
        Returns:
            True if unsubscribed, False if not found
        """
        # Find subscriber
        query = select(Subscriber).where(Subscriber.email == email)
        subscriber = (await self.db.execute(query)).scalar_one_or_none()
        
        if not subscriber:
            return False
        
        # Set as inactive
        subscriber.is_active = False
        await self.db.commit()
        
        return True
