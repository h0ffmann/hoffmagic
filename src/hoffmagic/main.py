"""
Main application entry point for HoffMagic Blog.
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse

from hoffmagic.config import settings
from hoffmagic.logger import setup_logging
from hoffmagic.db.engine import init_db
from hoffmagic.api.routes import blog, essays, about, contact

# Set up logging
logger = setup_logging()

# Create FastAPI application
app = FastAPI(
    title="hoffmagic blog",
    description="a beautiful python-based blog application",
    version="0.1.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# Mount static files
app.mount("/static", StaticFiles(directory="src/hoffmagic/static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="src/hoffmagic/templates")

# Include all API routes
app.include_router(blog.router, prefix="/api/blog", tags=["blog"])
app.include_router(essays.router, prefix="/api/essays", tags=["essays"])
app.include_router(about.router, prefix="/api/about", tags=["about"])
app.include_router(contact.router, prefix="/api/contact", tags=["contact"])


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
    return JSONResponse({"status": "ok"})


@app.get("/")
async def home(request: Request):
    """
    Render the home page.
    """
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "hoffmagic blog"}
    )


@app.get("/blog")
async def blog_page(request: Request):
    """
    Render the blog listing page.
    """
    return templates.TemplateResponse(
        "blog/list.html", 
        {"request": request, "title": "blog | hoffmagic"}
    )


@app.get("/blog/{slug}")
async def blog_detail(request: Request, slug: str):
    """
    Render a specific blog post.
    """
    return templates.TemplateResponse(
        "blog/detail.html", 
        {"request": request, "slug": slug} # Title set in block title now
    )


@app.get("/essays")
async def essays_page(request: Request):
    """
    Render the essays listing page.
    """
    return templates.TemplateResponse(
        "essays/list.html", 
        {"request": request, "title": "essays | hoffmagic"}
    )


@app.get("/essays/{slug}")
async def essay_detail(request: Request, slug: str):
    """
    Render a specific essay.
    """
    return templates.TemplateResponse(
        "essays/detail.html", 
        {"request": request, "slug": slug} # Title set in block title now
    )


@app.get("/about")
async def about_page(request: Request):
    """
    Render the about page.
    """
    return templates.TemplateResponse(
        "about.html", 
        {"request": request, "title": "about me | hoffmagic"}
    )


@app.get("/contact")
async def contact_page(request: Request):
    """
    Render the contact page.
    """
    return templates.TemplateResponse(
        "contact.html", 
        {"request": request, "title": "contact | hoffmagic"}
    )
