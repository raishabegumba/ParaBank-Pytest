"""Pytest configuration and fixtures for UI tests."""
import pytest
from datetime import datetime
from src.utils.webdriver_utils import (
    get_browser,
    get_browser_context,
    create_screenshots_directory
)
from src.config.settings import settings


@pytest.fixture(scope="session")
def browser():
    """Initialize browser for the session."""
    create_screenshots_directory()
    playwright_browser = get_browser()
    yield playwright_browser
    playwright_browser.close()


@pytest.fixture(scope="function")
def page(browser):
    """Create a new page for each test."""
    context = get_browser_context(browser)
    page = context.new_page()
    page.goto(settings.base_url)
    yield page
    
    # Teardown
    context.close()


@pytest.fixture(scope="session")
def test_env():
    """Return test environment from settings."""
    return settings.test_env


def pytest_runtest_makereport(item, call):
    """Make test report with failure info."""
    if call.excinfo is not None:
        item.rep_call = item


@pytest.fixture(scope="session", autouse=True)
def cleanup():
    """Cleanup after test run."""
    yield
    # Cleanup code here if needed
