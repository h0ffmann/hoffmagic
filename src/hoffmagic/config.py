"""
Configuration management for HoffMagic Blog.
"""
from typing import List, Optional
from pathlib import Path
import os

from pydantic import PostgresDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables with fallbacks.
    """
    # Base settings
    ENV: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str
    BASE_DIR: Path = Path(__file__).parent.parent.parent.resolve()
    CONTENT_DIR: Path = BASE_DIR / "content"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # Database settings
    DATABASE_URL: PostgresDsn
    
    # Content settings
    BLOG_DIR: Path = CONTENT_DIR / "blog"
    ESSAYS_DIR: Path = CONTENT_DIR / "essays"
    
    # Cache settings
    CACHE_TTL: int = 60 * 5  # 5 minutes

    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse ALLOWED_HOSTS from string to list, handling JSON or comma-separated."""
        if isinstance(v, str):
            # Try to parse as JSON first
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # If that fails, try to parse as comma-separated list
                return [host.strip() for host in v.split(",") if host.strip()]
        return v
    
    @validator("BLOG_DIR", "ESSAYS_DIR", "CONTENT_DIR")
    def create_dirs(cls, v):
        """Ensure directories exist."""
        os.makedirs(v, exist_ok=True)
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # Explicitly set to default (False)
    )


# Create settings instance
settings = Settings()
