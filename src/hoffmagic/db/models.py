"""
SQLAlchemy ORM models for HoffMagic Blog.
"""
import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean, Column, ForeignKey, Integer, String, 
    Text, DateTime, Table, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from hoffmagic.db.engine import Base


# Many-to-many relationship between posts and tags
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Post(Base):
    """
    Represents a blog post or essay.
    """
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    is_published = Column(Boolean, default=False)
    is_essay = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    publish_date = Column(DateTime(timezone=True), nullable=True)
    featured_image = Column(String(255), nullable=True)
    
    # Relationships
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    author = relationship("Author", back_populates="posts")
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")


class Author(Base):
    """
    Represents a blog author.
    """
    __tablename__ = "authors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    bio = Column(Text, nullable=True)
    avatar = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    
    # Relationships
    posts = relationship("Post", back_populates="author")


class Tag(Base):
    """
    Represents a content tag or category.
    """
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    
    # Relationships
    posts = relationship("Post", secondary=post_tags, back_populates="tags")


class Comment(Base):
    """
    Represents a blog comment.
    """
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    author_name = Column(String(100), nullable=False)
    author_email = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_approved = Column(Boolean, default=False)
    
    # Relationships
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    post = relationship("Post", back_populates="comments")
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    replies = relationship(
        "Comment", 
        backref=ForeignKey("parent_id"),
        remote_side=[id],
        cascade="all, delete-orphan"
    )


class Subscriber(Base):
    """
    Represents a newsletter subscriber.
    """
    __tablename__ = "subscribers"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ContactMessage(Base):
    """
    Represents a contact form submission.
    """
    __tablename__ = "contact_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_read = Column(Boolean, default=False)
