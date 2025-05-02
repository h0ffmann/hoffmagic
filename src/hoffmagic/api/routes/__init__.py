# This file ensures the routes directory is recognized as a Python package
from fastapi import APIRouter
from .blog import router as blog_router
from .essays import router as essays_router
from .about import router as about_router
from .contact import router as contact_router

# Create main router (can be used to group API routes under /api)
api_router = APIRouter(prefix="/api")

# Register all route modules with the main API router
api_router.include_router(blog_router, prefix="/blog", tags=["blog"])
api_router.include_router(essays_router, prefix="/essays", tags=["essays"])
api_router.include_router(about_router, prefix="/about", tags=["about"])
api_router.include_router(contact_router, prefix="/contact", tags=["contact"])
