"""
Comprehensive UI test suite for ParaBank Bill Pay page.
Focus: end-to-end flows, validation, business rules, confirmation accuracy.
"""

import pytest
from datetime import datetime, timedelta
from playwright.sync_api import Page

from src.pages.bill_pay_page import BillPayPage
from src.pages.login_page import LoginPage
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.bill_pay
class TestBillPayComprehensive:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.page = page
        self.bill_pay_page = BillPayPage(page)
        self.login_page = LoginPage(page)

    # =========================================================
    # HELPERS
    # =========================================================

    def login_and_navigate(self):
        self.login_page.navigate_to_login()

        result = self.login_page.login_with_validation("john", "demo")
        assert result["success"], "Login failed"

        self.bill_pay_page.navigate_to_bill_pay()
        self.bill_pay_page.assert_bill_pay_page_loaded()

    def payee_data(self):
        return {
            "name": "Test Payee",
            "address": "456 Payee Street",
            "city": "Payee City",
            "state": "NY",
            "zip_code": "54321",
            "phone": "5559876543",
            "account_number": "987654321",
        }

    # =========================================================
    # SMOKE / BASIC FLOW
    # =========================================================

    @pytest.mark.smoke
    def test_bill_pay_page_loads(self):
        self.login_and_navigate()

        title = self.page.title()
        assert "ParaBank" in title

        assert self.bill_pay_page.is_visible(self.bill_pay_page.FROM_ACCOUNT_SELECT)
        assert self.bill_pay_page.is_visible(self.bill_pay_page.AMOUNT_FIELD)
        assert self.bill_pay_page.is_visible(self.bill_pay_page.SEND_PAYMENT_BUTTON)

    @pytest.mark.smoke
    def test_accounts_dropdown_populates(self):
        self.login_and_navigate()

        accounts = self.bill_pay_page.get_available_accounts()
        assert isinstance(accounts, list)
        assert len(accounts) > 0, "No accounts available for bill pay"

    @pytest.mark.smoke
    def test_successful_payment_new_payee(self):
        self.login_and_navigate()

        accounts = self.bill_pay_page.get_available_accounts()
        assert len(accounts) > 0

        # FIX: send_payment() does not accept date/description/add_new_payee —
        # those fields do not exist on the real ParaBank bill-pay form.
        self.bill_pay_page.send_payment(
            from_account=accounts[0],
            amount="100.00",
            payee_info=self.payee_data(),
        )

        assert self.bill_pay_page.wait_for_payment_complete()
        assert self.bill_pay_page.is_payment_successful()
        assert "Bill Payment Complete" in self.bill_pay_page.get_success_message()

    # =========================================================
    # NEGATIVE VALIDATION
    # =========================================================

    @pytest.mark.regression
    @pytest.mark.regression
    def test_zero_amount_rejected(self):
        """Verify validation logic rejects zero amount."""
        self.login_and_navigate()

        validation = self.bill_pay_page.validate_payment_limits(0.00)

        assert validation["within_transaction_limit"] is False
        assert "greater than 0" in " ".join(validation["issues"])


    @pytest.mark.regression
    def test_negative_amount_rejected(self):
        """Verify validation logic rejects negative amount."""
        self.login_and_navigate()

        validation = self.bill_pay_page.validate_payment_limits(-10.00)

        assert validation["within_transaction_limit"] is False
        assert "greater than 0" in " ".join(validation["issues"])

    @pytest.mark.regression
    def test_invalid_amount_format_rejected(self):
        self.login_and_navigate()

        accounts = self.bill_pay_page.get_available_accounts()
        assert accounts

        self.bill_pay_page.send_payment(
            from_account=accounts[0],
            amount="abc",
            payee_info=self.payee_data(),
        )

        assert not self.bill_pay_page.is_payment_successful()

    # =========================================================
    # FORM VALIDATION LOGIC
    # =========================================================

    @pytest.mark.usability
    def test_payment_form_validation_state(self):
        self.login_and_navigate()

        # Empty form must not be ready
        validation = self.bill_pay_page.validate_payment_form()
        assert validation["form_ready"] is False

        accounts = self.bill_pay_page.get_available_accounts()
        self.bill_pay_page.select_from_account(accounts[0])
        self.bill_pay_page.enter_payment_amount("100.00")
        self.bill_pay_page.fill_payee_information(**self.payee_data())

        validation = self.bill_pay_page.validate_payment_form()

        # FIX: date_entered / valid_date keys were removed from
        # validate_payment_form() — the real form has no date field.
        assert validation["form_ready"]
        assert validation["valid_amount"]
        assert validation["payee_info_complete"]

    # =========================================================
    # BUSINESS RULES
    # =========================================================

    @pytest.mark.usability
    def test_payment_limits(self):
        self.login_and_navigate()

        # FIX: corrected assertion logic — amounts ≤ $5,000 are within the
        # transaction limit; amounts > $5,000 are not.
        test_cases = [
            (0.01,    True,  True),   # valid: within both limits
            (100.00,  True,  True),   # valid
            (5000.00, True,  True),   # at transaction limit — still valid
            (5001.00, False, True),   # over transaction limit
            (20000.00, False, False), # over both limits
        ]

        for amount, expect_txn, expect_daily in test_cases:
            result = self.bill_pay_page.validate_payment_limits(amount)
            assert result["within_transaction_limit"] is expect_txn, (
                f"transaction_limit mismatch for {amount}"
            )
            assert result["within_daily_limit"] is expect_daily, (
                f"daily_limit mismatch for {amount}"
            )

    # =========================================================
    # ERROR HANDLING
    # =========================================================

    @pytest.mark.error_handling
    def test_empty_form_submission_fails(self):
        self.login_and_navigate()

        self.bill_pay_page.click_send_payment()

        assert not self.bill_pay_page.is_payment_successful()

        error = self.bill_pay_page.get_error_message()
        log.info(f"Error message: {error}")

    # =========================================================
    # FORM OPERATIONS
    # =========================================================

    @pytest.mark.regression
    def test_clear_payment_form(self):
        self.login_and_navigate()

        accounts = self.bill_pay_page.get_available_accounts()
        self.bill_pay_page.select_from_account(accounts[0])
        self.bill_pay_page.enter_payment_amount("120.00")
        self.bill_pay_page.fill_payee_information(**self.payee_data())

        self.bill_pay_page.clear_payment_form()

        # FIX: removed check for PAYMENT_DATE_FIELD (does not exist on
        # the real form). Verify only the amount field is cleared.
        amount = self.bill_pay_page.get_attribute(
            self.bill_pay_page.AMOUNT_FIELD, "value"
        )
        assert amount in ["", None], "Amount field should be empty after clear"

    # =========================================================
    # CONFIRMATION DATA
    # =========================================================

    @pytest.mark.data_validation
    def test_payment_confirmation_parsing(self):
        self.login_and_navigate()

        accounts = self.bill_pay_page.get_available_accounts()
        assert accounts

        amount = "75.25"

        self.bill_pay_page.send_payment(
            from_account=accounts[0],
            amount=amount,
            payee_info=self.payee_data(),
        )

        if self.bill_pay_page.is_payment_successful():
            details = self.bill_pay_page.get_payment_confirmation_details()
            assert isinstance(details, dict)

            if "amount" in details:
                assert amount in details["amount"]

    # =========================================================
    # WAIT / SYNCHRONIZATION
    # =========================================================

    @pytest.mark.regression
    def test_payment_completion_wait(self):
        self.login_and_navigate()

        accounts = self.bill_pay_page.get_available_accounts()

        self.bill_pay_page.send_payment(
            from_account=accounts[0],
            amount="50.00",
            payee_info=self.payee_data(),
        )

        assert self.bill_pay_page.wait_for_payment_complete(timeout=10000)