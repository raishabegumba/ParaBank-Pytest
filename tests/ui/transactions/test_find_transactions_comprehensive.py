"""Comprehensive Find Transactions test suite."""

import pytest
from datetime import datetime, timedelta
from playwright.sync_api import Page

from src.pages.find_transactions_page import FindTransactionsPage
from src.pages.login_page import LoginPage
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.find_transactions
@pytest.mark.comprehensive
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

    def get_date_string(self, days_offset: int = 0):
        target_date = datetime.now() + timedelta(days=days_offset)
        return target_date.strftime("%m/%d/%Y")

    @pytest.mark.regression
    def test_search_transactions_with_invalid_date_format(self):
        self.login_and_navigate()

        account_id = self.find_transactions_page.get_available_accounts()[0]

        self.find_transactions_page.search_transactions(
            account_id=account_id,
            date="invalid-date"
        )

        self.find_transactions_page.wait_for_search_results()

    @pytest.mark.regression
    def test_search_transactions_with_invalid_amount_format(self):
        self.login_and_navigate()

        account_id = self.find_transactions_page.get_available_accounts()[0]

        self.find_transactions_page.search_transactions(
            account_id=account_id,
            amount="abc"
        )

        self.find_transactions_page.wait_for_search_results()

    @pytest.mark.regression
    def test_search_transactions_with_future_date(self):
        self.login_and_navigate()

        account_id = self.find_transactions_page.get_available_accounts()[0]

        self.find_transactions_page.search_transactions(
            account_id=account_id,
            date=self.get_date_string(30)
        )

        self.find_transactions_page.wait_for_search_results()

    @pytest.mark.data_validation
    def test_transaction_data_structure(self):
        self.login_and_navigate()

        account_id = self.find_transactions_page.get_available_accounts()[0]

        self.find_transactions_page.search_transactions(account_id=account_id)

        if self.find_transactions_page.wait_for_search_results():

            transactions = self.find_transactions_page.get_transactions()

            assert isinstance(transactions, list)

            if transactions:
                transaction = transactions[0]

                required_fields = [
                    "transaction_id",
                    "date",
                    "description",
                    "deposit",
                    "withdrawal"
                ]

                for field in required_fields:
                    assert field in transaction

    @pytest.mark.data_validation
    def test_transaction_count_accuracy(self):
        self.login_and_navigate()

        account_id = self.find_transactions_page.get_available_accounts()[0]

        self.find_transactions_page.search_transactions(account_id=account_id)

        if self.find_transactions_page.wait_for_search_results():

            count = self.find_transactions_page.get_transaction_count()
            transactions = self.find_transactions_page.get_transactions()

            assert count == len(transactions)

    @pytest.mark.advanced_search
    def test_search_transactions_with_multiple_criteria(self):
        self.login_and_navigate()

        account_id = self.find_transactions_page.get_available_accounts()[0]

        transaction_type = (
            self.find_transactions_page.get_transaction_types()[0]
        )

        self.find_transactions_page.search_transactions(
            account_id=account_id,
            transaction_type=transaction_type,
            from_date=self.get_date_string(-30),
            to_date=self.get_date_string(),
            amount="50.00"
        )

        assert self.find_transactions_page.wait_for_search_results()

    @pytest.mark.data_export
    def test_transaction_data_export(self):
        self.login_and_navigate()

        account_id = self.find_transactions_page.get_available_accounts()[0]

        self.find_transactions_page.search_transactions(account_id=account_id)

        if self.find_transactions_page.wait_for_search_results():

            export_data = (
                self.find_transactions_page.export_transaction_data()
            )

            assert isinstance(export_data, dict)
            assert "transactions" in export_data
            assert "search_criteria" in export_data

    @pytest.mark.integration
    def test_complete_transaction_search_workflow(self):
        self.login_and_navigate()

        account_id = self.find_transactions_page.get_available_accounts()[0]

        transaction_type = (
            self.find_transactions_page.get_transaction_types()[0]
        )

        self.find_transactions_page.search_transactions(
            account_id=account_id
        )

        assert self.find_transactions_page.wait_for_search_results()

        self.find_transactions_page.search_transactions(
            account_id=account_id,
            transaction_type=transaction_type
        )

        assert self.find_transactions_page.wait_for_search_results()

        self.find_transactions_page.search_transactions(
            account_id=account_id,
            transaction_type=transaction_type,
            from_date=self.get_date_string(-7),
            to_date=self.get_date_string()
        )

        assert self.find_transactions_page.wait_for_search_results()