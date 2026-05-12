"""Pytest configuration for loan request page UI tests."""
import pytest
from src.pages.loan_request_page import LoanRequestPage


@pytest.fixture
def loan_request_page(page):
    """Initialize loan request page object."""
    return LoanRequestPage(page)
