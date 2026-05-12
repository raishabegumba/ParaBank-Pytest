"""Pytest configuration and fixtures for API tests."""
import pytest
from src.api.base_api import BaseAPI
from src.config.settings import settings


@pytest.fixture
def api_client():
    """Initialize API client."""
    client = BaseAPI(settings.api_base_url)
    yield client
    client.close_session()


@pytest.fixture
def api_headers():
    """Return common API headers."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
