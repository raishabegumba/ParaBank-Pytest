"""Pytest configuration for bill pay page UI tests."""
import pytest
from src.pages.bill_pay_page import BillPayPage


@pytest.fixture
def bill_pay_page(page):
    """Initialize bill pay page object."""
    return BillPayPage(page)
