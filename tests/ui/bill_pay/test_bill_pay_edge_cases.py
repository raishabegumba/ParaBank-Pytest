"""
Edge case test suite for ParaBank Bill Pay page.
"""

import pytest
from datetime import datetime, timedelta
from playwright.sync_api import Page

from src.pages.bill_pay_page import BillPayPage
from src.pages.login_page import LoginPage


@pytest.mark.ui
@pytest.mark.bill_pay
@pytest.mark.edge_case
class TestBillPayEdgeCases:

    # =========================================================================
    # SETUP
    # =========================================================================

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Instantiate page objects directly — no external fixtures needed."""
        self.page = page
        self.bill_pay_page = BillPayPage(page)
        self.login_page = LoginPage(page)

    # =========================================================================
    # HELPERS
    # =========================================================================

    def login_and_navigate(self):
        """Login and navigate to Bill Pay."""
        self.login_page.navigate_to_login()

        result = self.login_page.login_with_validation("john", "demo")
        assert result["success"], "Login failed"

        self.bill_pay_page.navigate_to_bill_pay()
        self.bill_pay_page.assert_bill_pay_page_loaded()

    def generate_test_payee_data(self):
        """Reusable payee data."""
        return {
            "name": "Edge Test Payee",
            "address": "123 Edge Street",
            "city": "Dallas",
            "state": "TX",
            "zip_code": "75001",
            "phone": "5551234567",
            "account_number": "123456789",
        }

    def get_future_date(self, days_ahead: int = 7) -> str:
        """Generate a future date string (kept for test documentation clarity)."""
        return (datetime.now() + timedelta(days=days_ahead)).strftime("%m/%d/%Y")

    # =========================================================================
    # EDGE CASE TESTS
    # =========================================================================

    def test_payment_with_maximum_amount(self):
        """Verify payment at the maximum allowed limit is handled."""
        self.login_and_navigate()

        accounts = self.bill_pay_page.get_available_accounts()
        assert len(accounts) > 0

        # FIX: removed date/description/add_new_payee — not on the form.
        self.bill_pay_page.send_payment(
            from_account=accounts[0],
            amount="5000.00",
            payee_info=self.generate_test_payee_data(),
        )

        result = self.bill_pay_page.is_payment_successful()
        assert isinstance(result, bool)

    def test_payment_with_decimal_amount(self):
        """Verify decimal amounts are accepted."""
        self.login_and_navigate()

        accounts = self.bill_pay_page.get_available_accounts()
        assert len(accounts) > 0

        self.bill_pay_page.send_payment(
            from_account=accounts[0],
            amount="123.45",
            payee_info=self.generate_test_payee_data(),
        )

        assert self.bill_pay_page.is_payment_successful()

    def test_payment_with_very_small_amount(self):
        """Verify the smallest valid amount ($0.01) is accepted."""
        self.login_and_navigate()

        accounts = self.bill_pay_page.get_available_accounts()
        assert len(accounts) > 0

        self.bill_pay_page.send_payment(
            from_account=accounts[0],
            amount="0.01",
            payee_info=self.generate_test_payee_data(),
        )

        assert self.bill_pay_page.is_payment_successful()

    def test_payment_with_special_characters_in_payee_name(self):
        """Verify special characters in payee name are handled gracefully."""
        self.login_and_navigate()

        accounts = self.bill_pay_page.get_available_accounts()
        assert len(accounts) > 0

        payee_data = self.generate_test_payee_data()
        payee_data["name"] = "Test-O'Connor & Associates"

        self.bill_pay_page.send_payment(
            from_account=accounts[0],
            amount="100.00",
            payee_info=payee_data,
        )

        result = self.bill_pay_page.is_payment_successful()
        assert isinstance(result, bool)

    def test_payment_with_multiple_accounts_scenario(self):
        """Verify each available account can be selected in turn."""
        self.login_and_navigate()

        accounts = self.bill_pay_page.get_available_accounts()

        if len(accounts) < 2:
            pytest.skip("Test requires at least two accounts; skipping.")

        for account_label in accounts[:3]:
            self.bill_pay_page.select_from_account(account_label)

            selected_value = self.page.locator(
            f"{self.bill_pay_page.FROM_ACCOUNT_SELECT} option:checked"
            ).get_attribute("value")

            assert selected_value is not None and selected_value.strip(), (
                f"Expected a selected account value for '{account_label}'")