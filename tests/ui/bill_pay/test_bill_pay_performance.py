"""Performance UI test suite for ParaBank Bill Pay page."""

import pytest
from datetime import datetime, timedelta

from src.pages.bill_pay_page import BillPayPage
from src.pages.login_page import LoginPage


@pytest.mark.ui
@pytest.mark.bill_pay
@pytest.mark.performance
class TestBillPayPerformance:
    """Performance-focused bill pay tests."""

    PAGE_LOAD_THRESHOLD = 5.0
    DROPDOWN_LOAD_THRESHOLD = 2.0
    FORM_OPERATION_THRESHOLD = 3.0

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
        """Reusable login helper."""

        self.login_page.navigate_to_login()

        result = self.login_page.login_with_validation(
            "john",
            "demo"
        )

        assert result["success"]

        self.bill_pay_page.navigate_to_bill_pay()
        self.bill_pay_page.assert_bill_pay_page_loaded()

    def generate_test_payee_data(self):
        """Generate test payee data."""

        return {
            "name": "Performance Payee",
            "address": "123 Performance Street",
            "city": "Performance City",
            "state": "TX",
            "zip_code": "75001",
            "phone": "5559998888",
            "account_number": "PERF001"
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
    # PERFORMANCE TESTS
    # =========================================================

    def test_bill_pay_page_load_performance(self):
        """Verify page load performance."""

        start_time = datetime.now()

        self.login_and_navigate_to_bill_pay()

        load_time = (
            datetime.now() - start_time
        ).total_seconds()

        assert (
            load_time < self.PAGE_LOAD_THRESHOLD
        ), (
            f"Page load time "
            f"{load_time}s exceeded "
            f"{self.PAGE_LOAD_THRESHOLD}s"
        )

    def test_account_dropdown_population_performance(self):
        """Verify account dropdown load speed."""

        self.login_and_navigate_to_bill_pay()

        start_time = datetime.now()

        accounts = (
            self.bill_pay_page
            .get_available_accounts()
        )

        load_time = (
            datetime.now() - start_time
        ).total_seconds()

        assert len(accounts) > 0

        assert (
            load_time
            < self.DROPDOWN_LOAD_THRESHOLD
        ), (
            f"Dropdown load time "
            f"{load_time}s exceeded "
            f"{self.DROPDOWN_LOAD_THRESHOLD}s"
        )

    def test_payment_form_fill_performance(self):
        """Verify form filling performance."""

        self.login_and_navigate_to_bill_pay()

        accounts = (
            self.bill_pay_page
            .get_available_accounts()
        )

        assert len(accounts) > 0

        start_time = datetime.now()

        self.bill_pay_page.select_from_account(
            accounts[0]
        )

        self.bill_pay_page.enter_payment_amount(
            "100.00"
        )

        self.bill_pay_page.fill_payee_information(
            **self.generate_test_payee_data()
        )

        execution_time = (
            datetime.now() - start_time
        ).total_seconds()

        assert (
            execution_time
            < self.FORM_OPERATION_THRESHOLD
        ), (
            f"Form fill time "
            f"{execution_time}s exceeded "
            f"{self.FORM_OPERATION_THRESHOLD}s"
        )
        
    def test_payment_submission_performance(self):
        """Verify payment submission timing."""

        self.login_and_navigate_to_bill_pay()

        accounts = (
            self.bill_pay_page
            .get_available_accounts()
        )

        assert len(accounts) > 0

        start_time = datetime.now()

        self.bill_pay_page.send_payment(
            from_account=accounts[0],
            amount="20.00",
            payee_info=self.generate_test_payee_data(),
            add_new_payee=True
        )

        completion_time = (
            datetime.now() - start_time
        ).total_seconds()

        assert (
            completion_time < 10.0
        ), (
            f"Payment submission took "
            f"{completion_time}s"
        )

    def test_multiple_account_selection_performance(self):
        """Verify repeated account selection speed."""

        self.login_and_navigate_to_bill_pay()

        accounts = (
            self.bill_pay_page
            .get_available_accounts()
        )

        assert len(accounts) > 0

        test_accounts = accounts[:3]

        start_time = datetime.now()

        for account in test_accounts:

            self.bill_pay_page.select_from_account(
                account
            )

        execution_time = (
            datetime.now() - start_time
        ).total_seconds()

        assert execution_time < 3.0

    def test_form_validation_performance(self):
        """Verify validation execution speed."""

        self.login_and_navigate_to_bill_pay()

        start_time = datetime.now()

        validation = (
            self.bill_pay_page
            .validate_payment_form()
        )

        execution_time = (
            datetime.now() - start_time
        ).total_seconds()

        assert isinstance(validation, dict)

        assert execution_time < 1.0

    def test_clear_form_performance(self):
        """Verify clear form operation speed."""

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

        start_time = datetime.now()

        self.bill_pay_page.clear_payment_form()

        execution_time = (
            datetime.now() - start_time
        ).total_seconds()

        assert execution_time < 2.0

    def test_repeated_form_operations_stability(self):
        """Verify repeated operations remain stable."""

        self.login_and_navigate_to_bill_pay()

        accounts = (
            self.bill_pay_page
            .get_available_accounts()
        )

        assert len(accounts) > 0

        start_time = datetime.now()

        for _ in range(5):

            self.bill_pay_page.select_from_account(
                accounts[0]
            )

            self.bill_pay_page.enter_payment_amount(
                "10.00"
            )

            self.bill_pay_page.clear_payment_form()

        execution_time = (
            datetime.now() - start_time
        ).total_seconds()

        assert execution_time < 10.0