# This file ensures the routes directory is recognized as a Python package
from fastapi import APIRouter, Depends, Query
from typing import Optional

# Create main router (can be used to group API routes under /api)
# Note: The individual route files (blog.py, essays.py, etc.) already define their own routers.
# This api_router might not be strictly necessary if app.include_router is used directly in main.py
# as is currently the case. Keeping it based on the diff provided.
api_router = APIRouter(prefix="/api")

# If you intended to include the specific routers here instead of main.py, you would do:
# from . import blog, essays, contact, about # etc.
# api_router.include_router(blog.router)
# api_router.include_router(essays.router)
# api_router.include_router(contact.router)
# api_router.include_router(about.router)
# Then in main.py: app.include_router(api_router)
