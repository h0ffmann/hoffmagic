"""
Pydantic schemas for API data validation.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl, constr


# Base schemas
class TagBase(BaseModel):
    name: str
    slug: str


class AuthorBase(BaseModel):
    name: str
    bio: Optional[str] = None
    avatar: Optional[str] = None
    email: EmailStr


class PostBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    is_published: bool = False
    is_essay: bool = False
    featured_image: Optional[str] = None


class CommentBase(BaseModel):
    content: str
    author_name: str
    author_email: EmailStr


class SubscriberBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class ContactMessageBase(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str


# Create schemas
class TagCreate(TagBase):
    pass


class AuthorCreate(AuthorBase):
    pass


class PostCreate(PostBase):
    slug: str
    author_id: int
    tag_ids: Optional[List[int]] = None


class CommentCreate(CommentBase):
    post_id: int
    parent_id: Optional[int] = None


class SubscriberCreate(SubscriberBase):
    pass


class ContactMessageCreate(ContactMessageBase):
    pass


# Update schemas
class TagUpdate(TagBase):
    name: Optional[str] = None
    slug: Optional[str] = None


class AuthorUpdate(AuthorBase):
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[EmailStr] = None


class PostUpdate(PostBase):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    is_published: Optional[bool] = None
    is_essay: Optional[bool] = None
    featured_image: Optional[str] = None
    slug: Optional[str] = None
    author_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None


class CommentUpdate(CommentBase):
    content: Optional[str] = None
    author_name: Optional[str] = None
    author_email: Optional[EmailStr] = None
    is_approved: Optional[bool] = None


class SubscriberUpdate(SubscriberBase):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None


class ContactMessageUpdate(BaseModel):
    is_read: Optional[bool] = None


# Read schemas
class TagRead(TagBase):
    id: int

    class Config:
        from_attributes = True


class AuthorRead(AuthorBase):
    id: int
    
    class Config:
        from_attributes = True


class CommentRead(CommentBase):
    id: int
    created_at: datetime
    is_approved: bool
    post_id: int
    parent_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class PostRead(PostBase):
    id: int
    slug: str
    created_at: datetime
    updated_at: datetime
    publish_date: Optional[datetime] = None
    author_id: int
    author: AuthorRead
    tags: List[TagRead] = []
    
    class Config:
        from_attributes = True


class PostDetailRead(PostRead):
    comments: List[CommentRead] = []
    
    class Config:
        from_attributes = True


class SubscriberRead(SubscriberBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContactMessageRead(ContactMessageBase):
    id: int
    created_at: datetime
    is_read: bool
    
    class Config:
        from_attributes = True


# Response schemas
class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    pages: int
    items: List[BaseModel]


class BlogPostsResponse(PaginatedResponse):
    items: List[PostRead]


class EssaysResponse(PaginatedResponse):
    items: List[PostRead]


class TagsResponse(PaginatedResponse):
    items: List[TagRead]


class CommentsResponse(PaginatedResponse):
    items: List[CommentRead]


class SubscribersResponse(PaginatedResponse):
    items: List[SubscriberRead]


class ContactMessagesResponse(PaginatedResponse):
    items: List[ContactMessageRead]


# Error response
class ErrorResponse(BaseModel):
    detail: str
