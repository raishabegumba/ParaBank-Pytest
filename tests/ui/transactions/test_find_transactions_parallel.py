"""Parallel-safe Find Transactions tests."""

import pytest
from playwright.sync_api import Page

from src.pages.find_transactions_page import FindTransactionsPage
from src.pages.login_page import LoginPage


@pytest.mark.parallel
@pytest.mark.ui
@pytest.mark.find_transactions
class TestFindTransactionsParallel:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.page = page
        self.find_transactions_page = FindTransactionsPage(page)
        self.login_page = LoginPage(page)

    def login_and_navigate(self):
        self.login_page.navigate_to_login()

        login_result = self.login_page.login_with_validation(
            "john",
            "demo"
        )

        assert login_result["success"]

        self.find_transactions_page.navigate_to_find_transactions()

    def test_parallel_account_search(self):
        self.login_and_navigate()

        accounts = self.find_transactions_page.get_available_accounts()

        for account in accounts[:3]:
            self.find_transactions_page.search_transactions(
                account_id=account
            )

            assert self.find_transactions_page.wait_for_search_results()

    def test_parallel_transaction_type_search(self):
        self.login_and_navigate()

        account_id = (
            self.find_transactions_page.get_available_accounts()[0]
        )

        transaction_types = (
            self.find_transactions_page.get_transaction_types()
        )

        for transaction_type in transaction_types[:3]:

            self.find_transactions_page.search_transactions(
                account_id=account_id,
                transaction_type=transaction_type
            )

            assert self.find_transactions_page.wait_for_search_results()

    def test_parallel_search_results_loading(self):
        self.login_and_navigate()

        account_id = (
            self.find_transactions_page.get_available_accounts()[0]
        )

        self.find_transactions_page.search_transactions(
            account_id=account_id
        )

        assert self.find_transactions_page.wait_for_search_results()

    def test_parallel_transaction_data_read(self):
        self.login_and_navigate()

        account_id = (
            self.find_transactions_page.get_available_accounts()[0]
        )

        self.find_transactions_page.search_transactions(
            account_id=account_id
        )

        if self.find_transactions_page.wait_for_search_results():

            transactions = (
                self.find_transactions_page.get_transactions()
            )

            assert isinstance(transactions, list)