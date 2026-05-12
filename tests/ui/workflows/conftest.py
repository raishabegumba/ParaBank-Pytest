"""Pytest configuration for workflow and integration UI tests."""
import pytest
from src.pages.login_page import LoginPage
from src.pages.registration_page import RegistrationPage
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.pages.transfer_funds_page import TransferFundsPage
from src.pages.bill_pay_page import BillPayPage
from src.pages.open_account_page import OpenAccountPage
from src.pages.loan_request_page import LoanRequestPage
from src.pages.find_transactions_page import FindTransactionsPage


@pytest.fixture
def login_page(page):
    """Initialize login page object."""
    return LoginPage(page)


@pytest.fixture
def registration_page(page):
    """Initialize registration page object."""
    return RegistrationPage(page)


@pytest.fixture
def accounts_overview_page(page):
    """Initialize accounts overview page object."""
    return AccountsOverviewPage(page)


@pytest.fixture
def transfer_funds_page(page):
    """Initialize transfer funds page object."""
    return TransferFundsPage(page)


@pytest.fixture
def bill_pay_page(page):
    """Initialize bill pay page object."""
    return BillPayPage(page)


@pytest.fixture
def open_account_page(page):
    """Initialize open account page object."""
    return OpenAccountPage(page)


@pytest.fixture
def loan_request_page(page):
    """Initialize loan request page object."""
    return LoanRequestPage(page)


@pytest.fixture
def find_transactions_page(page):
    """Initialize find transactions page object."""
    return FindTransactionsPage(page)
