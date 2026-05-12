"""Pytest configuration for accounts page UI tests."""
import pytest
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.pages.open_account_page import OpenAccountPage


@pytest.fixture
def accounts_overview_page(page):
    """Initialize accounts overview page object."""
    return AccountsOverviewPage(page)


@pytest.fixture
def open_account_page(page):
    """Initialize open account page object."""
    return OpenAccountPage(page)
