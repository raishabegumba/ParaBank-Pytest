"""
Edge case tests for ParaBank Loan Request page.

Covers boundary amounts (min/max), decimal precision, zero down payment,
and multi-application flows within the same session.
"""
import pytest
from playwright.sync_api import Page
from src.pages.loan_request_page import LoanRequestPage
from src.pages.login_page import LoginPage
from src.utils.test_data_utils import TestDataUtils
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.loan_request
@pytest.mark.edge_case
class TestLoanRequestEdgeCases:
    """Edge case tests — boundary values, unusual inputs, and multi-step flows."""

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
    #  Boundary amounts                                                    #
    # ------------------------------------------------------------------ #

    def test_loan_application_with_maximum_amount(self):
        """Maximum allowed loan amount ($100,000) completes processing."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            self.loan_page.apply_for_loan("100000.00", "10000.00", accounts[0])
            assert self.loan_page.wait_for_loan_processing_complete(), \
                "Loan processing should complete"
            log.info(
                f"Max-amount loan: {'Approved' if self.loan_page.is_loan_approved() else 'Denied'}"
            )

    def test_loan_application_with_minimum_amount(self):
        """Minimum allowed loan amount ($1,000) completes processing."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            self.loan_page.apply_for_loan("1000.00", "100.00", accounts[0])
            assert self.loan_page.wait_for_loan_processing_complete(), \
                "Loan processing should complete"
            log.info(
                f"Min-amount loan: {'Approved' if self.loan_page.is_loan_approved() else 'Denied'}"
            )

    # ------------------------------------------------------------------ #
    #  Decimal precision                                                   #
    # ------------------------------------------------------------------ #

    def test_loan_application_with_decimal_amounts(self):
        """Decimal loan and down payment amounts are accepted and processed."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            self.loan_page.apply_for_loan("12345.67", "1234.56", accounts[0])
            assert self.loan_page.wait_for_loan_processing_complete(), \
                "Loan processing should complete with decimal amounts"

    # ------------------------------------------------------------------ #
    #  Zero down payment                                                   #
    # ------------------------------------------------------------------ #

    def test_loan_application_with_zero_down_payment(self):
        """Zero down payment is accepted for submission (result is likely a denial)."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            self.loan_page.apply_for_loan("10000.00", "0.00", accounts[0])
            assert self.loan_page.wait_for_loan_processing_complete(), \
                "Loan processing should complete"
            log.info(
                f"Zero-down loan: {'Approved' if self.loan_page.is_loan_approved() else 'Denied'}"
            )

    # ------------------------------------------------------------------ #
    #  Multi-application same session                                      #
    # ------------------------------------------------------------------ #

    def test_multiple_loan_applications_same_session(self):
        """Three sequential loan applications in the same session all return results."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()

        if len(accounts) > 0:
            scenarios = [
                ("5000.00",  "500.00"),
                ("7500.00",  "750.00"),
                ("15000.00", "1500.00"),
            ]
            results = []

            for loan_amount, down_payment in scenarios:
                self.loan_page.navigate_to_loan_request()
                self.loan_page.apply_for_loan(loan_amount, down_payment, accounts[0])

                if self.loan_page.wait_for_loan_processing_complete():
                    is_approved = self.loan_page.is_loan_approved()
                    results.append({
                        'loan_amount': loan_amount,
                        'down_payment': down_payment,
                        'approved': is_approved
                    })
                    log.info(
                        f"Loan {loan_amount}: {'Approved' if is_approved else 'Denied'}"
                    )

            assert len(results) == len(scenarios), \
                "Should have a result for every loan application"

    # ------------------------------------------------------------------ #
    #  JavaScript / browser compatibility                                  #
    # ------------------------------------------------------------------ #

    @pytest.mark.browser_compatibility
    def test_loan_request_form_javascript_functionality(self):
        """Form is accessible and fillable via JavaScript DOM manipulation."""
        self.login_and_navigate()

        form_exists = self.page.evaluate("""
            () => document.querySelector('#requestLoanForm') !== null
        """)

        assert form_exists, \
            "Loan request form should be accessible via JavaScript"

        accounts = self.loan_page.get_available_accounts()

        if len(accounts) > 0:
            self.page.evaluate(f"""
                () => {{
                    document.querySelector('#requestLoanForm #fromAccountId').value = '{accounts[0]}';
                    document.querySelector('#requestLoanForm #amount').value = '10000.00';
                    document.querySelector('#requestLoanForm #downPayment').value = '1000.00';
                }}
            """)

            validation = self.loan_page.validate_loan_request_form()

            assert validation['form_ready'], \
                "Form should be ready after JavaScript fill"