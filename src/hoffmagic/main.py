# -*- coding: utf-8 -*-
# type: ignore[name-defined] # ignore missing type hints for FastAPI

import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, AsyncGenerator
from datetime import datetime

import time # Add time import
import time # Add time import
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware # Add CORS Middleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Assuming engine and logger are setup elsewhere and imported if needed
# Assuming engine and logger are setup elsewhere and imported if needed
from .db.engine import SessionLocal, init_db, get_session # Add get_session
from .logger import setup_logging
from .api.routes import blog, essays, contact # Import API route modules

from sqlalchemy.ext.asyncio import AsyncSession

# Set up logging
# logger = logging.getLogger("hoffmagic") # Original - assumes setup elsewhere
logger = setup_logging()

# Define base directory *inside* the container based on WorkingDir
CONTAINER_APP_DIR = Path("/app")

app = FastAPI(
    title="Hoffmagic Blog",
    description="Hoffmann's magical blog.",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None, # Use settings from config
    redoc_url="/redoc" if settings.DEBUG else None, # Use settings from config
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for simplicity, adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(blog.router, prefix="/api/blog", tags=["blog"])
app.include_router(essays.router, prefix="/api/essays", tags=["essays"])
app.include_router(contact.router, prefix="/api/contact", tags=["contact"])

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"path: {request.url.path} | method: {request.method} | status: {response.status_code} | time: {process_time:.4f}s")
    return response

# --- Configure Template and Static paths using CONTAINER_APP_DIR ---
templates = Jinja2Templates(directory=CONTAINER_APP_DIR / "templates")
app.mount(
    "/static",
    StaticFiles(directory=CONTAINER_APP_DIR / "static"),
    name="static"
)
# -------------------------------------------------------------------

# Placeholder for your API routers - uncomment and implement later
# from .api.routes import about, blog, contact, essays

# @asynccontextmanager
# async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
#     """
#     Initialize database connection and perform startup tasks.
#     """
#     logger.info("Starting hoffmagic application")
#     await init_db()
#     yield
#     logger.info("Shutting down hoffmagic application")
#
# app = FastAPI(lifespan=lifespan) # Use lifespan if preferred over on_event

@app.on_event("startup")
async def startup_event() -> None:
    """
    Initialize database connection and perform startup tasks.
    """
    logger.info("starting hoffmagic application")
    await init_db()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Close database connection and perform cleanup tasks (if any needed besides what context managers handle).
    """
    logger.info("shutting down hoffmagic application")


@app.get("/health")
async def health_check() -> JSONResponse:
    """
    Health check endpoint for kubernetes/monitoring.
    """
    return JSONResponse(content={"status": "ok"})

# Define context processor for common template variables
async def common_context(request: Request):
    return {"request": request, "now": datetime.utcnow()}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    context = await common_context(request)
    return templates.TemplateResponse("index.html", context)

@app.get("/blog", response_class=HTMLResponse)
async def blog_page(request: Request):
    context = await common_context(request)
    # Fetch paginated posts in real implementation
    context["posts"] = [] # Placeholder
    return templates.TemplateResponse("blog/list.html", context)

@app.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_detail(request: Request, slug: str):
    # Fetch actual post data using slug later
    context = await common_context(request)
    context["post"] = {"title": "Sample Post", "slug": slug, "summary": "Summary here", "publish_date": datetime.utcnow(), "updated_at": datetime.utcnow(), "tags": [], "author": {"name": "Author"}} # Dummy data
    return templates.TemplateResponse("blog/detail.html", context)

@app.get("/essays", response_class=HTMLResponse)
async def essays_page(request: Request):
    context = await common_context(request)
    # Fetch paginated essays in real implementation
    context["essays"] = [] # Placeholder
    return templates.TemplateResponse("essays/list.html", context)

@app.get("/essays/{slug}", response_class=HTMLResponse)
async def essay_detail(request: Request, slug: str):
    # Fetch actual essay data using slug later
    context = await common_context(request)
    # Placeholder data structure matching the template usage
    context["essay"] = {
        "title": "Sample Essay", "slug": slug, "summary": "Essay summary.",
        "publish_date": datetime.utcnow(), "updated_at": datetime.utcnow(),
        "reading_time": 10, "featured_image": None, "content": "<p>Content here</p>",
        "tags": [{"name": "Tag1", "slug": "tag1"}],
        "author": {"name": "Author", "avatar": None, "bio": "Author bio", "email": "a@b.com"}
    }
    return templates.TemplateResponse("essays/detail.html", context)

@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
     # Fetch author/stats data later
    context = await common_context(request)
    # Dummy data matching template usage
    context["author"] = {"name": "Default Author", "avatar": None, "email": "a@b.com"}
    context["stats"] = {"post_count": 10, "essay_count": 2, "tag_count": 5, "comment_count": 20}
    return templates.TemplateResponse("about.html", context)

@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    context = await common_context(request)
    return templates.TemplateResponse("contact.html", context)

# API routers are now included above
