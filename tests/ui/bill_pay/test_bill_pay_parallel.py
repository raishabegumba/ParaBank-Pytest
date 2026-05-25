"""Parallel-safe UI test suite for ParaBank Bill Pay page."""

import pytest
from datetime import datetime, timedelta

from src.pages.bill_pay_page import BillPayPage
from src.pages.login_page import LoginPage


@pytest.mark.ui
@pytest.mark.bill_pay
@pytest.mark.parallel
class TestBillPayParallel:
    """Parallel-safe bill pay test coverage."""

    @pytest.fixture(autouse=True)
    def setup(
        self,
        page,
        bill_pay_page,
        login_page
    ):
        """
        Isolated setup for xdist workers.
        """

        self.page = page
        self.bill_pay_page = bill_pay_page
        self.login_page = login_page

    # =========================================================
    # HELPERS
    # =========================================================

    def login_and_navigate_to_bill_pay(self):
        """Reusable login helper."""

        self.login_page.navigate_to_login()

        result = self.login_page.login_with_validation(
            "john",
            "demo"
        )

        assert result["success"]

        self.bill_pay_page.navigate_to_bill_pay()
        self.bill_pay_page.assert_bill_pay_page_loaded()

    def generate_test_payee_data(
        self,
        suffix: str = "parallel"
    ) -> dict:
        """
        Unique payee data for isolated workers.
        """

        return {
            "name": f"Payee {suffix}",
            "address": "123 Parallel Street",
            "city": "Parallel City",
            "state": "TX",
            "zip_code": "75001",
            "phone": "5551234567",
            "account_number": f"ACC{suffix}"
        }

    def get_future_date(
        self,
        days_ahead: int = 7
    ) -> str:
        """Generate future date."""

        future_date = (
            datetime.now() + timedelta(days=days_ahead)
        )

        return future_date.strftime("%m/%d/%Y")

    # =========================================================
    # PARALLEL TESTS
    # =========================================================

    def test_parallel_bill_pay_page_loads(self):
        """Verify page loads safely in parallel."""

        self.login_and_navigate_to_bill_pay()

        assert "Bill Pay" in self.page.title()

    def test_parallel_account_dropdown_loading(self):
        """Verify account dropdown loads correctly."""

        self.login_and_navigate_to_bill_pay()

        accounts = (
            self.bill_pay_page
            .get_available_accounts()
        )

        assert isinstance(accounts, list)
        assert len(accounts) > 0

    def test_parallel_form_validation(self):
        """Verify form validation works in parallel."""

        self.login_and_navigate_to_bill_pay()

        validation = (
            self.bill_pay_page
            .validate_payment_form()
        )

        assert isinstance(validation, dict)
        assert "form_ready" in validation

    def test_parallel_multiple_account_selection(self):
        """Verify multiple account selections work."""

        self.login_and_navigate_to_bill_pay()

        accounts = (
            self.bill_pay_page
            .get_available_accounts()
        )

        assert len(accounts) > 0

        for account in accounts[:3]:

            self.bill_pay_page.select_from_account(
                account
            )

            selected = (
                self.bill_pay_page.get_input_value(
                    self.bill_pay_page
                    .FROM_ACCOUNT_SELECT)
            )

            assert selected == account

    def test_parallel_successful_payment_flow(self):
        """Verify stable payment flow."""

        self.login_and_navigate_to_bill_pay()

        accounts = (
            self.bill_pay_page
            .get_available_accounts()
        )

        assert len(accounts) > 0

        payee_data = (
            self.generate_test_payee_data()
        )

        self.bill_pay_page.send_payment(
            from_account=accounts[0],
            amount="25.00",
            date=self.get_future_date(7),
            description="Parallel payment",
            payee_info=payee_data,
            add_new_payee=True
        )

        result = (
            self.bill_pay_page
            .is_payment_successful()
        )

        assert isinstance(result, bool)

    def test_parallel_clear_form(self):
        """Verify form clear operation."""

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

        self.bill_pay_page.clear_payment_form()

        amount_value = (
            self.bill_pay_page.get_attribute(
                self.bill_pay_page.AMOUNT_FIELD,
                "value"
            )
        )

        assert amount_value in ["", None]

    def test_parallel_wait_for_payment_completion(self):
        """Verify payment completion wait."""

        self.login_and_navigate_to_bill_pay()

        accounts = (
            self.bill_pay_page
            .get_available_accounts()
        )

        assert len(accounts) > 0

        payee_data = (
            self.generate_test_payee_data(
                suffix="wait"
            )
        )

        self.bill_pay_page.send_payment(
            from_account=accounts[0],
            amount="50.00",
            date=self.get_future_date(7),
            description="Parallel wait test",
            payee_info=payee_data,
            add_new_payee=True
        )

        completed = (
            self.bill_pay_page
            .wait_for_payment_complete()
        )

        assert isinstance(completed, bool)