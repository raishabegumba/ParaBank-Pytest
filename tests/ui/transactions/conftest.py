"""Pytest configuration for find transactions page UI tests."""
import pytest
from src.pages.find_transactions_page import FindTransactionsPage


@pytest.fixture
def find_transactions_page(page):
    """Initialize find transactions page object."""
    return FindTransactionsPage(page)
