"""
Performance tests for ParaBank Loan Request page.

Validates that page load and key interactions complete within defined
time thresholds. Thresholds are configurable via settings if needed.
"""
import pytest
from datetime import datetime
from playwright.sync_api import Page
from src.pages.loan_request_page import LoanRequestPage
from src.pages.login_page import LoginPage
from src.utils.test_data_utils import TestDataUtils
from src.config.logger import log


# Thresholds (seconds) — adjust via settings if environment-specific values are needed
PAGE_LOAD_THRESHOLD      = 5.0   # Full login + navigation to loan page
DROPDOWN_THRESHOLD       = 2.0   # Account dropdown population after page load
PROCESSING_THRESHOLD     = 10.0  # Loan processing end-to-end


@pytest.mark.ui
@pytest.mark.loan_request
@pytest.mark.performance
class TestLoanRequestPerformance:
    """Performance tests — response time thresholds for key user flows."""

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
    #  Page load                                                           #
    # ------------------------------------------------------------------ #

    def test_loan_request_page_load_performance(self):
        """Full login + page navigation completes within PAGE_LOAD_THRESHOLD seconds."""
        start = datetime.now()
        self.login_and_navigate()
        elapsed = (datetime.now() - start).total_seconds()

        log.info(f"Page load time: {elapsed:.3f}s (threshold: {PAGE_LOAD_THRESHOLD}s)")
        assert elapsed < PAGE_LOAD_THRESHOLD, \
            f"Page load time {elapsed:.3f}s exceeds {PAGE_LOAD_THRESHOLD}s threshold"

    # ------------------------------------------------------------------ #
    #  Dropdown population                                                 #
    # ------------------------------------------------------------------ #

    def test_account_dropdown_population_performance(self):
        """Account dropdown populates within DROPDOWN_THRESHOLD seconds."""
        self.login_and_navigate()

        start = datetime.now()
        accounts = self.loan_page.get_available_accounts()
        elapsed = (datetime.now() - start).total_seconds()

        log.info(
            f"Dropdown population: {elapsed:.3f}s (threshold: {DROPDOWN_THRESHOLD}s) "
            f"— {len(accounts)} account(s)"
        )
        assert elapsed < DROPDOWN_THRESHOLD, \
            f"Dropdown population time {elapsed:.3f}s exceeds {DROPDOWN_THRESHOLD}s threshold"

    # ------------------------------------------------------------------ #
    #  Loan processing response time                                       #
    # ------------------------------------------------------------------ #

    def test_loan_processing_response_time(self):
        """Loan processing (submit → result) completes within PROCESSING_THRESHOLD seconds."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()

        if len(accounts) > 0:
            self.loan_page.enter_loan_amount("10000.00")
            self.loan_page.enter_down_payment("1000.00")
            self.loan_page.select_from_account(accounts[0])

            start = datetime.now()
            self.loan_page.click_apply_for_loan()
            completed = self.loan_page.wait_for_loan_processing_complete()
            elapsed = (datetime.now() - start).total_seconds()

            log.info(
                f"Loan processing time: {elapsed:.3f}s (threshold: {PROCESSING_THRESHOLD}s)"
            )
            assert completed, "Loan processing should complete"
            assert elapsed < PROCESSING_THRESHOLD, \
                f"Loan processing time {elapsed:.3f}s exceeds {PROCESSING_THRESHOLD}s threshold"

    # ------------------------------------------------------------------ #
    #  Consecutive load check                                              #
    # ------------------------------------------------------------------ #

    def test_consecutive_page_navigations_performance(self):
        """Three consecutive navigations to the loan page each stay within threshold."""
        self.login_and_navigate()

        for i in range(1, 4):
            start = datetime.now()
            self.loan_page.navigate_to_loan_request()
            self.loan_page.assert_loan_request_page_loaded()
            elapsed = (datetime.now() - start).total_seconds()

            log.info(f"Navigation #{i}: {elapsed:.3f}s")
            assert elapsed < PAGE_LOAD_THRESHOLD, \
                f"Navigation #{i} took {elapsed:.3f}s, exceeds {PAGE_LOAD_THRESHOLD}s threshold"