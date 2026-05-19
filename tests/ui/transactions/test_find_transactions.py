"""Core UI test suite for ParaBank Find Transactions page."""

import pytest
from datetime import datetime, timedelta
from playwright.sync_api import Page

from src.pages.find_transactions_page import FindTransactionsPage
from src.pages.login_page import LoginPage
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.find_transactions
class TestFindTransactions:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.page = page
        self.find_transactions_page = FindTransactionsPage(page)
        self.login_page = LoginPage(page)
        self.accounts_page = AccountsOverviewPage(page)

    def login_and_navigate(self):
        self.login_page.navigate_to_login()

        login_result = self.login_page.login_with_validation("john", "demo")
        assert login_result["success"]

        self.find_transactions_page.navigate_to_find_transactions()
        self.find_transactions_page.assert_find_transactions_page_loaded()

    def get_date_string(self, days_offset: int = 0) -> str:
        target_date = datetime.now() + timedelta(days=days_offset)
        return target_date.strftime("%m/%d/%Y")

    @pytest.mark.smoke
    def test_find_transactions_page_loads_correctly(self):
        self.login_and_navigate()

        assert "ParaBank" in self.page.title()

    @pytest.mark.smoke
    def test_account_dropdown_populates_correctly(self):
        self.login_and_navigate()

        accounts = self.find_transactions_page.get_available_accounts()

        assert isinstance(accounts, list)
        assert len(accounts) > 0

    @pytest.mark.smoke
    def test_transaction_type_dropdown_populates_correctly(self):
        self.login_and_navigate()

        transaction_types = self.find_transactions_page.get_transaction_types()

        assert isinstance(transaction_types, list)
        assert len(transaction_types) > 0

    @pytest.mark.smoke
    def test_search_transactions_by_account(self):
        self.login_and_navigate()

        accounts = self.find_transactions_page.get_available_accounts()

        account_id = accounts[0]

        self.find_transactions_page.search_transactions(account_id=account_id)

        assert self.find_transactions_page.wait_for_search_results()

    @pytest.mark.smoke
    def test_search_transactions_by_date(self):
        self.login_and_navigate()

        accounts = self.find_transactions_page.get_available_accounts()

        self.find_transactions_page.search_transactions(
            account_id=accounts[0],
            date=self.get_date_string()
        )

        assert self.find_transactions_page.wait_for_search_results()

    @pytest.mark.smoke
    def test_search_transactions_by_date_range(self):
        self.login_and_navigate()

        accounts = self.find_transactions_page.get_available_accounts()

        self.find_transactions_page.search_transactions(
            account_id=accounts[0],
            from_date=self.get_date_string(-30),
            to_date=self.get_date_string()
        )

        assert self.find_transactions_page.wait_for_search_results()

    @pytest.mark.regression
    def test_clear_search_form(self):
        self.login_and_navigate()

        accounts = self.find_transactions_page.get_available_accounts()
        transaction_types = self.find_transactions_page.get_transaction_types()

        self.find_transactions_page.select_account(accounts[0])
        self.find_transactions_page.select_transaction_type(transaction_types[0])

        self.find_transactions_page.enter_date(self.get_date_string())
        self.find_transactions_page.enter_amount("100.00")

        self.find_transactions_page.clear_search_form()

        validation = self.find_transactions_page.validate_search_criteria()

        assert not validation["account_selected"]

    @pytest.mark.navigation
    def test_accounts_overview_link_navigation(self):
        self.login_and_navigate()

        self.find_transactions_page.click_accounts_overview()

        self.accounts_page.assert_accounts_overview_loaded()