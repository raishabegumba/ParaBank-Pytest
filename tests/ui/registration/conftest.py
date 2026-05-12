"""Pytest configuration for registration page UI tests."""
import pytest
from src.pages.registration_page import RegistrationPage


@pytest.fixture
def registration_page(page):
    """Initialize registration page object."""
    return RegistrationPage(page)
