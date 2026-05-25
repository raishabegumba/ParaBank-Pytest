"""
Parallel-safe tests for ParaBank Loan Request page.

These tests are designed to run concurrently without shared state conflicts.
Each test is fully self-contained: isolated login, independent account selection,
no dependency on execution order or side effects from other tests.

Run with: pytest -n auto tests/ui/loan/test_loan_parallel.py
"""
import pytest
from playwright.sync_api import Page
from src.pages.loan_request_page import LoanRequestPage
from src.pages.login_page import LoginPage
from src.utils.test_data_utils import TestDataUtils
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.loan_request
@pytest.mark.parallel
class TestLoanRequestParallel:
    """
    Parallel-safe tests — each test owns its own browser context and login session.

    Design rules for adding tests here:
      - No shared fixtures that mutate state across tests.
      - No dependency on test execution order.
      - No assertions that rely on account balance side effects from other tests.
    """

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.page = page
        self.loan_page = LoanRequestPage(page)
        self.login_page = LoginPage(page)
        self.test_data = TestDataUtils()

    def login_and_navigate(self):
        """Login and land on the loan request page."""
        self.login_page.navigate_to_login()
        result = self.login_page.login_with_validation("john", "demo")
        assert result['success'], "Login should be successful"
        self.loan_page.navigate_to_loan_request()
        self.loan_page.assert_loan_request_page_loaded()

    # ------------------------------------------------------------------ #
    #  Independent account selection scenarios                             #
    # ------------------------------------------------------------------ #

    def test_single_account_selection(self):
        """Single-account scenario: account is selected and reflected in the field."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) == 1:
            self.loan_page.select_from_account(accounts[0])
            selected = self.loan_page.get_input_value(
                self.loan_page.FROM_ACCOUNT_SELECT)
            assert selected == accounts[0], f"Account {accounts[0]} should be selected"

    def test_multiple_account_selection_first(self):
        """Multi-account scenario: first account can be selected independently."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) >= 2:
            self.loan_page.select_from_account(accounts[0])
            selected = self.loan_page.get_input_value(
                self.loan_page.FROM_ACCOUNT_SELECT)
            assert selected == accounts[0]

    def test_multiple_account_selection_second(self):
        """Multi-account scenario: second account can be selected independently."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) >= 2:
            self.loan_page.select_from_account(accounts[1])
            selected = self.loan_page.get_input_value(
                self.loan_page.FROM_ACCOUNT_SELECT)
            assert selected == accounts[1]

    def test_multiple_account_selection_third(self):
        """Multi-account scenario: third account can be selected independently."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) >= 3:
            self.loan_page.select_from_account(accounts[2])
            selected = self.loan_page.get_input_value(
                self.loan_page.FROM_ACCOUNT_SELECT)
            assert selected == accounts[2]

    # ------------------------------------------------------------------ #
    #  Independent loan amount submissions                                 #
    # ------------------------------------------------------------------ #

    def test_loan_submission_5000(self):
        """Independent loan submission for $5,000 completes without error."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            self.loan_page.apply_for_loan("5000.00", "500.00", accounts[0])
            completed = self.loan_page.wait_for_loan_processing_complete()
            assert completed, "Loan processing should complete"
            log.info(f"$5,000 loan: {'Approved' if self.loan_page.is_loan_approved() else 'Denied'}")

    def test_loan_submission_7500(self):
        """Independent loan submission for $7,500 completes without error."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            self.loan_page.apply_for_loan("7500.00", "750.00", accounts[0])
            completed = self.loan_page.wait_for_loan_processing_complete()
            assert completed, "Loan processing should complete"
            log.info(f"$7,500 loan: {'Approved' if self.loan_page.is_loan_approved() else 'Denied'}")

    def test_loan_submission_15000(self):
        """Independent loan submission for $15,000 completes without error."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            self.loan_page.apply_for_loan("15000.00", "1500.00", accounts[0])
            completed = self.loan_page.wait_for_loan_processing_complete()
            assert completed, "Loan processing should complete"
            log.info(f"$15,000 loan: {'Approved' if self.loan_page.is_loan_approved() else 'Denied'}")

    # ------------------------------------------------------------------ #
    #  Independent form validation checks                                  #
    # ------------------------------------------------------------------ #

    def test_form_ready_state_parallel(self):
        """Form transitions to ready state — safe to verify in parallel."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            self.loan_page.select_from_account(accounts[0])
            self.loan_page.enter_loan_amount("10000.00")
            self.loan_page.enter_down_payment("1000.00")
            validation = self.loan_page.validate_loan_request_form()
            assert validation['form_ready']

    def test_form_empty_state_parallel(self):
        """Fresh page form state is empty — safe to verify in parallel."""
        self.login_and_navigate()
        validation = self.loan_page.validate_loan_request_form()
        assert not validation['form_ready']
        assert not validation['loan_amount_entered']
        assert not validation['down_payment_entered']