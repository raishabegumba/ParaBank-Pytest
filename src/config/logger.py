"""Logger configuration for the test framework."""
import logging
import sys
from pathlib import Path
from loguru import logger

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def configure_logger(log_level: str = "INFO"):
    """Configure loguru logger for the test framework."""
    # Remove default handler
    logger.remove()

    # Console handler
    logger.add(
        sys.stdout,
        level=log_level,
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # File handler
    logger.add(
        LOG_DIR / "test_{time}.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="500 MB",
        retention="10 days",
    )

    return logger


# Initialize logger
log = configure_logger()
