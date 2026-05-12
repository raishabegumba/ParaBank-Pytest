"""Utility functions for common testing operations."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, BrowserContext
from src.config.settings import settings
from src.config.logger import log


def get_browser() -> Browser:
    """Initialize and return Playwright Browser."""
    playwright = sync_playwright().start()
    
    browser_type = settings.browser.lower()
    
    launch_args = {
        "headless": settings.headless,
    }

    if browser_type == "chrome":
        browser = playwright.chromium.launch(**launch_args)
    elif browser_type == "firefox":
        browser = playwright.firefox.launch(**launch_args)
    elif browser_type == "webkit":
        browser = playwright.webkit.launch(**launch_args)
    else:
        log.warning(f"Unknown browser {browser_type}, defaulting to chromium")
        browser = playwright.chromium.launch(**launch_args)

    log.info(f"Playwright {browser_type} browser initialized")
    return browser


def get_browser_context(browser: Browser) -> BrowserContext:
    """Get browser context with configured settings."""
    context = browser.new_context(
        viewport={
            "width": settings.window_width,
            "height": settings.window_height
        }
    )
    log.info(f"Browser context created with viewport {settings.window_width}x{settings.window_height}")
    return context


def wait_for_seconds(seconds: int):
    """Wait for specified seconds."""
    log.info(f"Waiting for {seconds} seconds...")
    time.sleep(seconds)


def create_screenshots_directory():
    """Create screenshots directory if it doesn't exist."""
    screenshot_dir = Path("reports/screenshots")
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    log.info(f"Screenshots directory ready: {screenshot_dir}")


def create_test_data_directory():
    """Create test data directory if it doesn't exist."""
    test_data_dir = Path("test_data")
    test_data_dir.mkdir(parents=True, exist_ok=True)
    log.info(f"Test data directory ready: {test_data_dir}")
