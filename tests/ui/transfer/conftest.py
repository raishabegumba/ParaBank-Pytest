"""Pytest configuration for transfer funds page UI tests."""
import pytest
from src.pages.transfer_funds_page import TransferFundsPage


@pytest.fixture
def transfer_funds_page(page):
    """Initialize transfer funds page object."""
    return TransferFundsPage(page)
