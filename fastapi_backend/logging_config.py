"""
Logging configuration for the application.
Sets up console and optional file logging with rotation.
"""

import logging
import logging.handlers
import os
from fastapi_backend.config import settings


def setup_logging() -> logging.Logger:
    """
    Configure application logging with console and optional file handler.
    Returns the configured logger.
    """
    logger = logging.getLogger("chatbot")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL, "INFO"))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL, "INFO"))
    handlers = [console_handler]
    
    # File handler (if enabled)
    if settings.LOG_FILE:
        os.makedirs(os.path.dirname(settings.LOG_FILE) or ".", exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=10_000_000,
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, settings.LOG_LEVEL, "INFO"))
        handlers.append(file_handler)
    
    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


logger = setup_logging()
