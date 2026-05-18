"""Pytest configuration and fixtures for UI tests."""
import pytest
from datetime import datetime
# from src.fixtures.browser_fixtures import *
# from src.fixtures.reporting_fixtures import *

from src.utils.webdriver_utils import (
    get_browser,
    get_browser_context,
    create_screenshots_directory
)
from src.config.settings import settings

pytest_plugins = [
    "src.fixtures.browser_fixtures",
    "src.fixtures.reporting_fixtures",
]

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
def initialize_parabank_db():
    """Reset ParaBank database before test session."""
    import requests
    try:
        response = requests.post(
            f"{settings.base_url}/services/bank/initializeDB",
            timeout=10
        )
        if response.status_code == 200:
            print("ParaBank DB initialized successfully")
        else:
            print(f"DB init returned status: {response.status_code}")
    except Exception as e:
        print(f"DB init failed (continuing anyway): {e}")
    yield


@pytest.fixture(scope="session", autouse=True)
def cleanup():
    """Cleanup after test run."""
    yield
    # Cleanup code here if needed