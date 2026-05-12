"""Pytest configuration for login page UI tests."""
import pytest
from src.pages.login_page import LoginPage


@pytest.fixture
def login_page(page):
    """Initialize login page object."""
    return LoginPage(page)
