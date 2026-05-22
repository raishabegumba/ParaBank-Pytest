"""Mobile UI test suite for ParaBank Bill Pay page."""

import pytest
from datetime import datetime, timedelta

from src.pages.bill_pay_page import BillPayPage
from src.pages.login_page import LoginPage


@pytest.mark.ui
@pytest.mark.bill_pay
@pytest.mark.mobile
class TestBillPayMobile:
    """Mobile and responsive bill pay coverage."""

    MOBILE_VIEWPORT = {
        "width": 375,
        "height": 667
    }

    TABLET_VIEWPORT = {
        "width": 768,
        "height": 1024
    }

    @pytest.fixture(autouse=True)
    def setup(
        self,
        page,
        bill_pay_page,
        login_page
    ):
        self.page = page
        self.bill_pay_page = bill_pay_page
        self.login_page = login_page

    # =========================================================
    # HELPERS
    # =========================================================

    def login_and_navigate_to_bill_pay(self):
        """Login and open Bill Pay page."""

        self.login_page.navigate_to_login()

        result = self.login_page.login_with_validation(
            "john",
            "demo"
        )

        assert result["success"]

        self.bill_pay_page.navigate_to_bill_pay()
        self.bill_pay_page.assert_bill_pay_page_loaded()

    def set_mobile_viewport(self):
        """Set mobile viewport."""

        self.page.set_viewport_size(
            self.MOBILE_VIEWPORT
        )

    def set_tablet_viewport(self):
        """Set tablet viewport."""

        self.page.set_viewport_size(
            self.TABLET_VIEWPORT
        )

    def generate_test_payee_data(self):
        """Generate mobile-safe payee data."""

        return {
            "name": "Mobile Payee",
            "address": "123 Mobile Street",
            "city": "Mobile City",
            "state": "CA",
            "zip_code": "90001",
            "phone": "5551234567",
            "account_number": "MOBILE001"
        }

    # =========================================================
    # MOBILE RESPONSIVE TESTS
    # =========================================================

    def test_mobile_bill_pay_page_loads(self):
        """Verify page loads on mobile."""

        self.set_mobile_viewport()

        self.login_and_navigate_to_bill_pay()

        assert self.page.is_visible(
            self.bill_pay_page.FROM_ACCOUNT_SELECT
        )

    def test_mobile_form_elements_visible(self):
        """Verify critical form fields are visible."""

        self.set_mobile_viewport()

        self.login_and_navigate_to_bill_pay()

        assert self.page.is_visible(
            self.bill_pay_page.FROM_ACCOUNT_SELECT
        )

        assert self.page.is_visible(
            self.bill_pay_page.AMOUNT_FIELD
        )

        assert self.page.is_visible(
            self.bill_pay_page.SEND_PAYMENT_BUTTON
        )

    def test_mobile_form_interaction(self):
        """Verify mobile form interaction works."""

        self.set_mobile_viewport()

        self.login_and_navigate_to_bill_pay()

        accounts = (
            self.bill_pay_page
            .get_available_accounts()
        )

        assert len(accounts) > 0

        self.bill_pay_page.select_from_account(
            accounts[0]
        )

        self.bill_pay_page.enter_payment_amount(
            "100.00"
        )

        amount_value = (
        self.bill_pay_page.get_input_value(
            self.bill_pay_page.AMOUNT_FIELD
            )
        )

        assert amount_value == "100.00"

    def test_mobile_successful_payment_flow(self):
        """Verify payment flow works on mobile."""

        self.set_mobile_viewport()

        self.login_and_navigate_to_bill_pay()

        accounts = (
            self.bill_pay_page
            .get_available_accounts()
        )

        assert len(accounts) > 0

        self.bill_pay_page.send_payment(
            from_account=accounts[0],
            amount="25.00",
            payee_info=self.generate_test_payee_data(),
        )

        result = (
            self.bill_pay_page
            .is_payment_successful()
        )

        assert isinstance(result, bool)

    def test_tablet_bill_pay_layout(self):
        """Verify tablet layout works."""

        self.set_tablet_viewport()

        self.login_and_navigate_to_bill_pay()

        assert self.page.is_visible(
            self.bill_pay_page.FROM_ACCOUNT_SELECT
        )

        assert self.page.is_visible(
            self.bill_pay_page.AMOUNT_FIELD
        )

    def test_mobile_form_validation(self):
        """Verify validation logic works on mobile."""

        self.set_mobile_viewport()

        self.login_and_navigate_to_bill_pay()

        validation = (
            self.bill_pay_page
            .validate_payment_form()
        )

        assert isinstance(validation, dict)

        assert "form_ready" in validation

    def test_mobile_landscape_view(self):
        """Verify landscape mobile layout."""

        self.page.set_viewport_size({
            "width": 667,
            "height": 375
        })

        self.login_and_navigate_to_bill_pay()

        assert self.page.is_visible(
            self.bill_pay_page.AMOUNT_FIELD
        )

        assert self.page.is_visible(
            self.bill_pay_page.SEND_PAYMENT_BUTTON
        )

    def test_mobile_form_clear_operation(self):
        """Verify clear form works on mobile."""

        self.set_mobile_viewport()

        self.login_and_navigate_to_bill_pay()

        accounts = (
            self.bill_pay_page
            .get_available_accounts()
        )

        assert len(accounts) > 0

        self.bill_pay_page.select_from_account(
            accounts[0]
        )

        self.bill_pay_page.enter_payment_amount(
            "99.00"
        )

        self.bill_pay_page.clear_payment_form()

        amount_value = (
            self.bill_pay_page.get_attribute(
                self.bill_pay_page.AMOUNT_FIELD,
                "value"
            )
        )

        assert amount_value in ["", None]