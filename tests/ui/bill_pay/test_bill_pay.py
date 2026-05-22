"""Base functional UI tests for ParaBank Bill Pay page."""

import pytest
from datetime import datetime, timedelta
from playwright.sync_api import Page

from src.pages.bill_pay_page import BillPayPage
from src.pages.login_page import LoginPage
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.bill_pay
class TestBillPay:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.page = page
        self.bill_pay_page = BillPayPage(page)
        self.login_page = LoginPage(page)

    # =========================================================
    # HELPERS
    # =========================================================

    def login_and_open_bill_pay(self):
        """Login and navigate to Bill Pay page."""
        self.login_page.navigate_to_login()

        result = self.login_page.login_with_validation("john", "demo")
        assert result["success"], "Login failed"

        self.bill_pay_page.navigate_to_bill_pay()
        self.bill_pay_page.assert_bill_pay_page_loaded()

    def payee_data(self):
        return {
            "name": "Test Payee",
            "address": "123 Main Street",
            "city": "NYC",
            "state": "NY",
            "zip_code": "10001",
            "phone": "1234567890",
            "account_number": "987654321",
        }

    # =========================================================
    # SMOKE TESTS
    # =========================================================

    @pytest.mark.smoke
    def test_bill_pay_page_loads(self):
        """Verify bill pay page loads successfully."""
        self.login_and_open_bill_pay()

        assert self.bill_pay_page.is_visible(self.bill_pay_page.FROM_ACCOUNT_SELECT)
        assert self.bill_pay_page.is_visible(self.bill_pay_page.AMOUNT_FIELD)
        assert self.bill_pay_page.is_visible(self.bill_pay_page.SEND_PAYMENT_BUTTON)

    @pytest.mark.smoke
    def test_accounts_dropdown_has_values(self):
        """Verify accounts dropdown is populated."""
        self.login_and_open_bill_pay()

        accounts = self.bill_pay_page.get_available_accounts()

        assert isinstance(accounts, list)
        assert len(accounts) > 0, "No accounts available"

    # =========================================================
    # FUNCTIONAL TESTS
    # =========================================================

    @pytest.mark.regression
    def test_successful_bill_payment(self):
        """Verify successful bill payment flow."""
        self.login_and_open_bill_pay()

        accounts = self.bill_pay_page.get_available_accounts()
        assert accounts

        # FIX: send_payment() does not accept date/description/add_new_payee;
        # payee_info is filled first so all fields are present before submit.
        self.bill_pay_page.send_payment(
            from_account=accounts[0],
            amount="100.00",
            payee_info=self.payee_data(),
        )

        success = (
            self.bill_pay_page.is_payment_successful()
            or self.bill_pay_page.wait_for_payment_complete()
        )

        assert success, "Payment did not complete successfully"

    @pytest.mark.regression
    def test_payment_without_account_fails(self):
        """Verify payment fails without selecting account.

        Note: ParaBank pre-selects the first account in the dropdown, so
        this test verifies the form still rejects a submission that is
        otherwise incomplete (no payee info).
        """
        self.login_and_open_bill_pay()

        # Intentionally skip select_from_account and payee info —
        # only enter the amount and attempt to submit.
        self.bill_pay_page.enter_payment_amount("100.00")
        self.bill_pay_page.click_send_payment()

        assert not self.bill_pay_page.is_payment_successful()

    @pytest.mark.regression
    def test_payment_without_amount_fails(self):
        """Verify payment fails without amount."""
        self.login_and_open_bill_pay()

        accounts = self.bill_pay_page.get_available_accounts()
        assert accounts

        self.bill_pay_page.select_from_account(accounts[0])
        self.bill_pay_page.fill_payee_information(**self.payee_data())
        # Deliberately skip enter_payment_amount
        self.bill_pay_page.click_send_payment()

        assert not self.bill_pay_page.is_payment_successful()

    @pytest.mark.regression
    def test_payment_with_invalid_amount_fails(self):
        """Verify invalid amount is rejected."""
        self.login_and_open_bill_pay()

        accounts = self.bill_pay_page.get_available_accounts()
        assert accounts

        self.bill_pay_page.send_payment(
            from_account=accounts[0],
            amount="abc",
            payee_info=self.payee_data(),
        )

        assert not self.bill_pay_page.is_payment_successful()

    # =========================================================
    # VALIDATION TESTS
    # =========================================================

    @pytest.mark.usability
    def test_payment_form_validation_state(self):
        """Verify form validation logic."""
        self.login_and_open_bill_pay()

        # Empty form must not be ready
        validation = self.bill_pay_page.validate_payment_form()
        assert validation["form_ready"] is False

        accounts = self.bill_pay_page.get_available_accounts()
        assert accounts

        self.bill_pay_page.select_from_account(accounts[0])
        self.bill_pay_page.enter_payment_amount("100.00")
        self.bill_pay_page.fill_payee_information(**self.payee_data())

        validation = self.bill_pay_page.validate_payment_form()

        assert validation["form_ready"] is True
        assert validation["valid_amount"] is True
        assert validation["payee_info_complete"] is True

    @pytest.mark.usability
    def test_payment_limit_validation(self):
        """Verify business rules for payment limits."""
        self.login_and_open_bill_pay()

        valid = self.bill_pay_page.validate_payment_limits(100.00)
        invalid = self.bill_pay_page.validate_payment_limits(20000.00)

        assert valid["within_transaction_limit"] is True
        assert invalid["within_transaction_limit"] is False

    # =========================================================
    # NAVIGATION TESTS
    # =========================================================

    @pytest.mark.navigation
    def test_navigation_to_accounts_overview(self):
        """Verify navigation link works."""
        self.login_and_open_bill_pay()

        self.bill_pay_page.click_accounts_overview()

        assert "overview" in self.page.url.lower()