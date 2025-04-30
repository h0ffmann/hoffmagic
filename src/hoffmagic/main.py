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
    title="HoffMagic Blog",
    description="A beautiful Python-based blog application",
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
    logger.info("Starting HoffMagic application")
    await init_db()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Close database connection and perform cleanup tasks.
    """
    logger.info("Shutting down HoffMagic application")


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
        {"request": request, "title": "HoffMagic Blog"}
    )


@app.get("/blog")
async def blog_page(request: Request):
    """
    Render the blog listing page.
    """
    return templates.TemplateResponse(
        "blog/list.html", 
        {"request": request, "title": "Blog | HoffMagic"}
    )


@app.get("/blog/{slug}")
async def blog_detail(request: Request, slug: str):
    """
    Render a specific blog post.
    """
    return templates.TemplateResponse(
        "blog/detail.html", 
        {"request": request, "title": "Blog Post | HoffMagic", "slug": slug}
    )


@app.get("/essays")
async def essays_page(request: Request):
    """
    Render the essays listing page.
    """
    return templates.TemplateResponse(
        "essays/list.html", 
        {"request": request, "title": "Essays | HoffMagic"}
    )


@app.get("/essays/{slug}")
async def essay_detail(request: Request, slug: str):
    """
    Render a specific essay.
    """
    return templates.TemplateResponse(
        "essays/detail.html", 
        {"request": request, "title": "Essay | HoffMagic", "slug": slug}
    )


@app.get("/about")
async def about_page(request: Request):
    """
    Render the about page.
    """
    return templates.TemplateResponse(
        "about.html", 
        {"request": request, "title": "About Me | HoffMagic"}
    )


@app.get("/contact")
async def contact_page(request: Request):
    """
    Render the contact page.
    """
    return templates.TemplateResponse(
        "contact.html", 
        {"request": request, "title": "Contact | HoffMagic"}
    )
