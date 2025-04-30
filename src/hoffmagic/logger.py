"""
Logging configuration for HoffMagic Blog.
"""
import logging
import sys
from typing import Any, Dict, Optional

from hoffmagic.config import settings


def setup_logging(
    name: str = "hoffmagic",
    level: Optional[int] = None,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """
    Set up application logging.
    
    Args:
        name: The logger name
        level: The log level
        format_string: The log format string
        
    Returns:
        A configured logger instance
    """
    # Set default level based on environment
    if level is None:
        level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    # Set default format string
    if format_string is None:
        if settings.ENV == "development":
            format_string = "%(levelname)s [%(name)s] %(message)s"
        else:
            format_string = "%(asctime)s - %(levelname)s [%(name)s] %(message)s"
    
    # Configure the logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create console handler if none exists
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        formatter = logging.Formatter(format_string)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
    
    # Disable propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger
