"""Comprehensive Find Transactions test suite."""

import pytest
from datetime import datetime, timedelta
from playwright.sync_api import Page

from src.pages.find_transactions_page import FindTransactionsPage
from src.pages.login_page import LoginPage
from src.config.logger import log


class TestFindTransactionsComprehensive:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.page = page
        self.find_transactions_page = FindTransactionsPage(page)
        self.login_page = LoginPage(page)

    def login_and_navigate(self):
        self.login_page.navigate_to_login()

        login_result = self.login_page.login_with_validation("john", "demo")
        assert login_result["success"]

        self.find_transactions_page.navigate_to_find_transactions()
        self.find_transactions_page.assert_find_transactions_page_loaded()

    def get_date_string(self, days_offset: int = 0):
        target_date = datetime.now() + timedelta(days=days_offset)
        return target_date.strftime("%m/%d/%Y")
    
    @pytest.mark.regression
    def test_search_transactions_with_invalid_date_format(self):
        self.login_and_navigate()

        account_id = (
            self.find_transactions_page
            .get_available_accounts()[0]
        )

        self.find_transactions_page.search_transactions(
            account_id=account_id,
            date="invalid-date"
        )

        assert self.page.url.endswith("findtrans.htm")
      

    @pytest.mark.regression
    def test_search_transactions_with_invalid_amount_format(self):
        self.login_and_navigate()

        account_id = (
            self.find_transactions_page
            .get_available_accounts()[0]
        )

        self.find_transactions_page.search_transactions(
            account_id=account_id,
            amount="abc"
        )

        validation = (
            self.find_transactions_page
            .validate_search_criteria()
        )

        assert validation["valid_amount"] is False
    
    @pytest.mark.regression
    def test_search_transactions_with_future_date(self):
        self.login_and_navigate()

        account_id = self.find_transactions_page.get_available_accounts()[0]

        self.find_transactions_page.search_transactions(
            account_id=account_id,
            date=self.get_date_string(30)
        )

        assert self.page.url.endswith("findtrans.htm")

    @pytest.mark.data_validation
    def test_transaction_data_structure(self):
        self.login_and_navigate()

        account_id = self.find_transactions_page.get_available_accounts()[0]

        self.find_transactions_page.search_transactions(
            account_id=account_id,
            from_date=self.get_date_string(-30),
            to_date=self.get_date_string()
        )

        assert self.page.url.endswith("findtrans.htm")

        transactions = self.find_transactions_page.get_transactions()

        assert isinstance(transactions, list)

        if transactions:
            transaction = transactions[0]

            required_fields = [
                "transaction_id",
                "date",
                "description",
                "deposit",
                "withdrawal",
                "row_index"
            ]

            for field in required_fields:
                assert field in transaction

    @pytest.mark.data_validation
    def test_transaction_count_accuracy(self):
        """Verify displayed transaction count matches returned data."""
        self.login_and_navigate()

        account_id = self.find_transactions_page.get_available_accounts()[0]

        self.find_transactions_page.search_transactions(
            account_id=account_id,
            from_date=self.get_date_string(-30),
            to_date=self.get_date_string()
        )

        assert self.page.url.endswith("findtrans.htm")

        count = self.find_transactions_page.get_transaction_count()
        transactions = self.find_transactions_page.get_transactions()

        assert count == len(transactions)

    @pytest.mark.advanced_search
    def test_search_transactions_with_multiple_criteria(self):
        self.login_and_navigate()

        account_id = self.find_transactions_page.get_available_accounts()[0]

        self.find_transactions_page.search_transactions(
            account_id=account_id,
            from_date=self.get_date_string(-30),
            to_date=self.get_date_string(),
            amount="50.00"
        )

        assert self.page.url.endswith("findtrans.htm")

    @pytest.mark.data_export
    def test_transaction_data_export(self):
        self.login_and_navigate()

        account_id = self.find_transactions_page.get_available_accounts()[0]

        self.find_transactions_page.search_transactions(
            account_id=account_id,
            from_date=self.get_date_string(-30),
            to_date=self.get_date_string()
        )

        assert self.page.url.endswith("findtrans.htm")

        export_data = (
            self.find_transactions_page.export_transaction_data()
        )

        assert isinstance(export_data, dict)
        assert "transactions" in export_data
        assert "search_criteria" in export_data
        assert "total_transactions" in export_data
        assert "timestamp" in export_data


    @pytest.mark.integration
    def test_complete_transaction_search_workflow(self):
        self.login_and_navigate()

        account_id = self.find_transactions_page.get_available_accounts()[0]

        # Search by account
        self.find_transactions_page.search_transactions(
            account_id=account_id,
            amount="50"
        )

        assert self.page.url.endswith("findtrans.htm")

        # Search by date
        self.find_transactions_page.navigate_to_find_transactions()

        self.find_transactions_page.search_transactions(
                account_id=account_id,
                date=self.get_date_string()
        )

        assert self.page.url.endswith("findtrans.htm")

        # Search by date range
        self.find_transactions_page.navigate_to_find_transactions()

        self.find_transactions_page.search_transactions(
            account_id=account_id,
            from_date=self.get_date_string(-7),
            to_date=self.get_date_string()
        )

        assert self.page.url.endswith("findtrans.htm")

    @pytest.mark.regression
    def test_clear_search_form(self):
        self.login_and_navigate()

        account_id = (
            self.find_transactions_page
            .get_available_accounts()[0]
        )

        self.find_transactions_page.select_account(account_id)

        self.find_transactions_page.enter_date(
            self.get_date_string()
        )

        self.find_transactions_page.enter_amount("100.00")

        self.find_transactions_page.enter_transaction_id("12345")

        self.find_transactions_page.clear_search_form()

        assert (
            self.page.locator(
                self.find_transactions_page.DATE_FIELD
            ).input_value() == ""
        )

        assert (
            self.page.locator(
                self.find_transactions_page.AMOUNT_FIELD
            ).input_value() == ""
        )

        assert (
            self.page.locator(
                self.find_transactions_page.TRANSACTION_ID_FIELD
            ).input_value() == ""
        )

    @pytest.mark.data_validation
    def test_validate_search_criteria(self):
        self.login_and_navigate()

        account_id = self.find_transactions_page.get_available_accounts()[0]

        self.find_transactions_page.select_account(account_id)
        self.find_transactions_page.enter_amount("100.00")

        validation = self.find_transactions_page.validate_search_criteria()

        assert validation["account_selected"] is True
        assert validation["valid_amount"] is True
        assert validation["search_ready"] is True