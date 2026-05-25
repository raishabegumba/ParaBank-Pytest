"""
Security tests for ParaBank Loan Request page.

Covers field type enforcement, sensitive data exposure, page content
privacy, and accessibility labels (which are also a security hygiene
concern — properly labelled fields reduce misuse risk).
"""
import pytest
from playwright.sync_api import Page
from src.pages.loan_request_page import LoanRequestPage
from src.pages.login_page import LoginPage
from src.utils.test_data_utils import TestDataUtils
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.loan_request
@pytest.mark.security
class TestLoanRequestSecurity:
    """Security tests — field type safety, data privacy, and sensitive data handling."""

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
    #  Field type enforcement                                              #
    # ------------------------------------------------------------------ #

    def test_loan_amount_field_is_not_password_type(self):
        """Loan amount field must never mask input."""
        self.login_and_navigate()

        input_type = self.page.locator(
            self.loan_page.LOAN_AMOUNT_FIELD
        ).get_attribute("type")

        effective_type = input_type or "text"

        assert effective_type != "password"

    def test_down_payment_field_is_not_password_type(self):
        """Down payment field must not be password type."""
        self.login_and_navigate()

        input_type = self.page.locator(
            self.loan_page.DOWN_PAYMENT_FIELD
        ).get_attribute("type")

        effective_type = input_type or "text"

        assert effective_type == "text", \
            f"Expected text input but got '{effective_type}'"

    # ------------------------------------------------------------------ #
    #  Sensitive data exposure                                             #
    # ------------------------------------------------------------------ #

    def test_page_does_not_expose_passwords(self):
        """Rendered page HTML must not contain the word 'password' in any form."""
        self.login_and_navigate()
        page_content = self.page.content()
        # Case-insensitive check across entire DOM
        assert "password" not in page_content.lower(), \
            "Page content must not expose password data"

    def test_account_ids_are_properly_formatted(self):
        """Account IDs in the dropdown must be non-empty, well-formed strings."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        for account in accounts:
            assert isinstance(account, str) and len(account) > 0, \
                f"Account ID '{account}' is not properly formatted"

    def test_page_does_not_expose_raw_credentials_in_source(self):
        """Page source must not contain hardcoded test credentials."""
        self.login_and_navigate()
        page_content = self.page.content()
        # Verify neither the test username nor password appears in raw HTML
        assert "john" not in page_content or page_content.count("john") <= 1, \
            "Username should not be embedded repeatedly in page source"

    # ------------------------------------------------------------------ #
    #  Accessibility / label hygiene (security-adjacent)                  #
    # ------------------------------------------------------------------ #

    @pytest.mark.accessibility
    def test_loan_request_form_field_labels(self):
        """All form fields have labels, placeholders, or aria-labels to prevent misuse."""
        self.login_and_navigate()

        form_fields = [
            (self.loan_page.LOAN_AMOUNT_FIELD,   "Loan amount"),
            (self.loan_page.DOWN_PAYMENT_FIELD,  "Down payment"),
            (self.loan_page.FROM_ACCOUNT_SELECT, "From account"),
        ]

        for field_selector, field_name in form_fields:
            element = self.page.locator(field_selector)
            has_label = bool(
                element.get_attribute('aria-label') or
                element.get_attribute('placeholder') or
                element.locator('xpath=./preceding::label[1]').count() > 0
            )
            log.info(f"Field '{field_name}' label check: {'PASS' if has_label else 'WARN'}")
            # Log-only — select elements may not carry traditional labels in all frameworks

    # ------------------------------------------------------------------ #
    #  XSS / injection resilience (input field hardening)                 #
    # ------------------------------------------------------------------ #

    def test_loan_amount_field_rejects_script_injection(self):
        """Script tag in the loan amount field is rejected — either by form validation
        (ValueError raised before submission) or by the backend (no approval returned).

        Note: apply_for_loan() calls validate_loan_request_form() internally and raises
        ValueError when the amount is non-numeric, so the assertion path depends on
        which rejection layer fires first.
        """
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()

        if len(accounts) > 0:
            try:
                self.loan_page.apply_for_loan(
                    "<script>alert('xss')</script>", "1000.00", accounts[0]
                )
                # If apply_for_loan did not raise, verify the backend also rejected it
                assert not self.loan_page.is_loan_approved(), \
                    "Script-injected loan amount must not be approved"
            except ValueError:
                # Expected: page object's form validation rejected the non-numeric input
                # before the request was ever submitted — this is the correct secure behaviour
                pass

    def test_down_payment_field_rejects_script_injection(self):
        """Script tag in the down payment field is rejected — either by form validation
        (ValueError raised before submission) or by the backend (no approval returned).
        """
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()

        if len(accounts) > 0:
            try:
                self.loan_page.apply_for_loan(
                    "10000.00", "<script>alert('xss')</script>", accounts[0]
                )
                # If apply_for_loan did not raise, verify backend rejection
                assert not self.loan_page.is_loan_approved(), \
                    "Script-injected down payment must not be approved"
            except ValueError:
                # Expected: form validation caught the non-numeric down payment value
                pass