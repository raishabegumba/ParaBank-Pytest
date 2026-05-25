"""
Core tests for ParaBank Loan Request page.

Covers the essential happy path and critical navigation flows.
Run these first — if any fail, the rest of the suite is likely broken.
"""
import pytest
from playwright.sync_api import Page
from src.pages.loan_request_page import LoanRequestPage
from src.pages.login_page import LoginPage
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.utils.test_data_utils import TestDataUtils


@pytest.mark.ui
@pytest.mark.loan_request
class TestLoanRequest:
    """Core smoke and navigation tests — fast gate before the full suite."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.page = page
        self.loan_page = LoanRequestPage(page)
        self.login_page = LoginPage(page)
        self.accounts_page = AccountsOverviewPage(page)
        self.test_data = TestDataUtils()

    def login_and_navigate(self):
        """Login and land on the loan request page."""
        self.login_page.navigate_to_login()
        result = self.login_page.login_with_validation("john", "demo")
        assert result['success'], "Login should be successful"
        self.loan_page.navigate_to_loan_request()
        self.loan_page.assert_loan_request_page_loaded()

    # ------------------------------------------------------------------ #
    #  Page load                                                           #
    # ------------------------------------------------------------------ #

    @pytest.mark.smoke
    def test_loan_request_page_loads_correctly(self):
        """Loan request page loads with the correct title."""
        self.login_and_navigate()
        assert "ParaBank" in self.page.title()
        assert "Loan" in self.page.title()

    @pytest.mark.smoke
    def test_account_dropdown_populates_correctly(self):
        """Account dropdown is populated with at least one account on page load."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        assert isinstance(accounts, list), "Accounts should be a list"
        assert len(accounts) > 0, "Should have at least one account"

    # ------------------------------------------------------------------ #
    #  Happy path                                                          #
    # ------------------------------------------------------------------ #

    @pytest.mark.smoke
    def test_successful_loan_application(self):
        """A valid loan application completes and returns either approval or denial."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            self.loan_page.apply_for_loan("10000.00", "1000.00", accounts[0])
            assert self.loan_page.wait_for_loan_processing_complete(), \
                "Loan processing should complete"
            assert self.loan_page.is_loan_approved() or self.loan_page.is_loan_denied(), \
                "Should get either approval or denial"

    def test_wait_for_loan_processing_complete(self):
        """Processing completes within the expected timeout after a valid submission."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            self.loan_page.apply_for_loan("10000.00", "1000.00", accounts[0])
            assert self.loan_page.wait_for_loan_processing_complete(), \
                "Loan processing should complete within timeout"

    # ------------------------------------------------------------------ #
    #  Navigation                                                          #
    # ------------------------------------------------------------------ #

    @pytest.mark.navigation
    def test_accounts_overview_link_navigation(self):
        """Accounts Overview link on the loan page navigates correctly."""
        self.login_and_navigate()
        self.loan_page.click_accounts_overview()
        self.accounts_page.assert_accounts_overview_loaded()