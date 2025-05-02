import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context # Import pass_context
import markdown as md
# Remove redundant markdown import if md is used consistently
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, FastAPI, Request, HTTPException # Ensure HTTPException is imported

from .api.routes import api_router
from .config import settings
from .db.engine import get_session, init_db
from .i18n import get_translations, DEFAULT_LANGUAGE
from .logger import setup_logging

logger = setup_logging()
CONTAINER_APP_DIR = Path("/app")
app = FastAPI(
    title="HoffMagic Blog",
    description="A beautiful blog built with FastAPI and Jinja2",
    version="0.1.0",
    debug=settings.DEBUG,
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing information."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"{request.client.host}:{request.client.port} - "
        f"\"{request.method} {request.url.path}\" {response.status_code} "
        f"- {process_time:.4f}s"
    )
    return response

# Include API routes
from hoffmagic.api.routes import api_router
app.include_router(api_router)

# Mount static files
app.mount(
    "/static",
    StaticFiles(directory=CONTAINER_APP_DIR / "static"),
    name="static",
)

# Setup Jinja2 templates
templates = Jinja2Templates(directory=CONTAINER_APP_DIR / "templates")
# Register markdown filter
templates.env.filters["markdown"] = lambda text: md.markdown(text, extensions=['extra', 'codehilite'])

# Define startup and shutdown events
@app.on_event("startup")
async def startup_event() -> None:
    """Initialize database connection and perform startup tasks."""
    logger.info("Starting up hoffmagic blog application")
    await init_db()
    logger.info("Database initialized")

@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Perform cleanup operations during shutdown."""
    logger.info("Shutting down hoffmagic blog application")

@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint for container orchestration."""
    return JSONResponse({"status": "healthy", "time": datetime.now().isoformat()})

async def common_context(request: Request) -> Dict[str, Any]:
    """Build common context data for templates.
    
    Args:
        request: The current request object
        
    Returns:
        Dict containing common template context variables
    """
    # Get language from query param, cookie, or default
    lang = request.query_params.get("lang", None)
    if not lang:
        lang = request.cookies.get("lang", DEFAULT_LANGUAGE)
        
    # Get translations for the selected language
    i18n = get_translations(lang)
    
    # Build common context
    context = {
        "request": request,
        "settings": settings,
        "lang": lang,
        "i18n": i18n,
        # We don't need to pass available_languages since we're hardcoding them in the template
        "year": datetime.now().year,
    }
    return context

@app.get("/", response_class=HTMLResponse, name="home")
async def home(
    request: Request, 
    db: AsyncSession = Depends(get_session)
) -> HTMLResponse:
    """Render the home page."""
    context = await common_context(request)
    return templates.TemplateResponse("index.html", context)

@app.get("/blog", response_class=HTMLResponse, name="blog_page")
async def blog_page(
    request: Request,
    page: int = 1,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_session)
) -> HTMLResponse:
    """Render the blog listing page."""
    from .services.blog import BlogService
    
    context = await common_context(request)
    blog_service = BlogService(db)
    
    # Get posts with pagination
    posts_response = await blog_service.get_posts(
        page=page,
        page_size=10,
        tag_slug=tag,
        search=search,
        is_essay=False
    )
    
    context["posts_response"] = posts_response
    return templates.TemplateResponse("blog/list.html", context)

@app.get("/blog/{slug}", response_class=HTMLResponse, name="blog_detail")
async def blog_detail(
    request: Request, 
    slug: str,
    db: AsyncSession = Depends(get_session)
) -> HTMLResponse:
    """Render a blog post detail page."""
    from .services.blog import BlogService
    
    context = await common_context(request)
    lang = context.get('lang', DEFAULT_LANGUAGE) # Get language from common context
    logger.debug(f"Rendering blog detail for slug: {slug}, lang: {lang}")

    blog_service = BlogService(db)
    # Pass lang to the service call
    post_data = await blog_service.get_post_by_slug(slug, is_essay=False, lang=lang)

    if not post_data or not post_data.is_published:
        logger.warning(f"Blog post not found or not published for slug: {slug}")
        # Use the standard 404 handler by raising HTTPException
        raise HTTPException(status_code=404, detail="Post not found")

    context.update({"post": post_data}) # Use update to add to existing context
    return templates.TemplateResponse("blog/detail.html", context)

@app.get("/essays", response_class=HTMLResponse, name="essays_page")
async def essays_page(
    request: Request,
    db: AsyncSession = Depends(get_session)
) -> HTMLResponse:
    """Render the essays listing page."""
    context = await common_context(request)
    return templates.TemplateResponse("essays/list.html", context)

@app.get("/essays/{slug}", response_class=HTMLResponse, name="essay_detail")
async def essay_detail(
    request: Request, 
    slug: str,
    db: AsyncSession = Depends(get_session)
) -> HTMLResponse:
    """Render an essay detail page."""
    from .services.essays import EssaysService
    
    context = await common_context(request)
    lang = context.get('lang', DEFAULT_LANGUAGE) # Get language from common context
    logger.debug(f"Rendering essay detail for slug: {slug}, lang: {lang}")

    essays_service = EssaysService(db)
    # Pass lang to the service call
    essay = await essays_service.get_essay_by_slug(slug, lang=lang)

    if not essay or not essay.is_published:
        logger.warning(f"Essay not found or not published for slug: {slug}")
        # Use the standard 404 handler by raising HTTPException
        raise HTTPException(status_code=404, detail="Essay not found")

    context.update({"essay": essay}) # Use update to add to existing context
    return templates.TemplateResponse("essays/detail.html", context)

@app.get("/about", response_class=HTMLResponse, name="about_page")
async def about_page(
    request: Request,
    db: AsyncSession = Depends(get_session)
) -> HTMLResponse:
    """Render the about page."""
    from .services.about import AboutService
    
    context = await common_context(request)
    about_service = AboutService(db)
    
    # Get author info
    author = await about_service.get_author_info()
    context["author"] = author
    
    # Get blog stats
    stats = await about_service.get_blog_stats()
    context["stats"] = stats
    
    return templates.TemplateResponse("about.html", context)

@app.get("/contact", response_class=HTMLResponse, name="contact_page")
async def contact_page(
    request: Request,
    db: AsyncSession = Depends(get_session)
) -> HTMLResponse:
    """Render the contact page."""
    context = await common_context(request)
    return templates.TemplateResponse("contact.html", context)

# Add error handlers for common HTTP errors
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 Not Found errors."""
    context = await common_context(request)
    context["error"] = {
        "code": 404,
        "message": context["i18n"].get("error_not_found", "Page not found")
    }
    return templates.TemplateResponse("error.html", context, status_code=404)

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    """Handle 500 Internal Server Error errors."""
    context = await common_context(request)
    context["error"] = {
        "code": 500,
        "message": context["i18n"].get("error_general", "An error occurred")
    }
    logger.error(f"Internal server error: {exc}")
    return templates.TemplateResponse("error.html", context, status_code=500)
