"""
Workflow test fixtures.
"""

import pytest
from playwright.sync_api import Page

from src.pages.login_page import LoginPage
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.config.settings import settings


# =============================================================================
# Core Page Fixtures
# =============================================================================

@pytest.fixture
def login_page(page: Page):
    """Return LoginPage instance."""
    return LoginPage(page)


@pytest.fixture
def accounts_page(page: Page):
    """Return AccountsOverviewPage instance."""
    return AccountsOverviewPage(page)


# =============================================================================
# Authentication Fixtures
# =============================================================================

@pytest.fixture
def authenticated_user():
    """Return default authenticated user credentials."""
    return {
        "username": settings.test_username,
        "password": settings.test_password,
    }


@pytest.fixture
def logged_in_page(
    page: Page,
    authenticated_user
):
    """
    Login user and return authenticated page instance.
    """
    login = LoginPage(page)

    login.navigate_to_login()

    login.login(
        authenticated_user["username"],
        authenticated_user["password"]
    )

    accounts_page = AccountsOverviewPage(page)

    accounts_page.verify_page_loaded()

    return page


# =============================================================================
# Business Workflow Fixtures
# =============================================================================

@pytest.fixture
def transfer_ready_accounts(
    logged_in_page
):
    """
    Return two valid accounts for transfer workflow testing.
    """
    accounts_page = AccountsOverviewPage(logged_in_page)

    accounts = accounts_page.get_all_accounts()

    assert len(accounts) >= 2, (
        "At least two accounts are required for transfer workflow tests."
    )

    return {
        "from_account": accounts[0]["account_id"],
        "to_account": accounts[1]["account_id"],
    }


# =============================================================================
# Dynamic Workflow Test Data
# =============================================================================

@pytest.fixture
def workflow_user_data(user_test_data):
    """
    Return a random user dataset for workflow testing.
    """
    user = user_test_data["random_users"][0]

    return {
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "address": user["address"],
        "city": user["city"],
        "state": user["state"],
        "zip_code": user["zip_code"],
        "phone": user["phone"],
        "ssn": user["ssn"],
        "username": user["username"],
        "password": user["password"],
        "confirm_password": user["password"],
    }


@pytest.fixture
def test_credentials():
    """Provide test credentials for error recovery tests."""
    return {
        "username": settings.test_username,
        "password": settings.test_password,
        "invalid_username": "invaliduser123",
        "invalid_password": "wrongpass",
    }


@pytest.fixture
def valid_bill_payment_data(bill_pay_test_data):
    """Provide valid bill payment data for tests."""
    return bill_pay_test_data.get("valid_payment", {
        "payee_name": "Test Payee",
        "payee_address": "123 Main St",
        "payee_city": "Test City",
        "payee_state": "TX",
        "payee_zip": "12345",
        "payee_phone": "5551234567",
        "payee_account": "987654321",
        "amount": 100.00,
        "from_account": None,  # Will be set by test
    })


@pytest.fixture
def valid_loan_data(loan_test_data):
    """Provide valid loan application data for tests."""
    return loan_test_data.get("valid_loan", {
        "loan_amount": 50000,
        "loan_term": 60,
        "loan_type": "PERSONAL",
        "down_payment": 10000,
    })