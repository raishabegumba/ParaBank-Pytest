"""Pytest configuration for security tests."""
import pytest
from src.config.settings import settings


@pytest.fixture(scope="session")
def test_credentials():
    """Provide test credentials for security tests."""
    return {
        'username': settings.test_username,
        'password': settings.test_password
    }
