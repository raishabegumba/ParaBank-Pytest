"""Core UI test suite for ParaBank Find Transactions page."""

import pytest
from datetime import datetime, timedelta
from playwright.sync_api import Page

from src.pages.find_transactions_page import FindTransactionsPage
from src.pages.login_page import LoginPage
from src.pages.accounts_overview_page import AccountsOverviewPage


@pytest.mark.ui
@pytest.mark.find_transactions
class TestFindTransactions:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Initialize test dependencies."""

        self.page = page

        self.find_transactions_page = FindTransactionsPage(page)
        self.login_page = LoginPage(page)
        self.accounts_page = AccountsOverviewPage(page)

    # =========================================================================
    # HELPERS
    # =========================================================================

    def login_and_navigate(self):
        """Login and navigate to Find Transactions page."""

        self.login_page.navigate_to_login()

        login_result = self.login_page.login_with_validation(
            "john",
            "demo"
        )

        assert login_result["success"], "Login failed"

        self.find_transactions_page.navigate_to_find_transactions()

        self.find_transactions_page.assert_find_transactions_page_loaded()

    def get_date_string(
        self,
        days_offset: int = 0
    ) -> str:
        """Generate formatted date string."""

        target_date = (
            datetime.now() + timedelta(days=days_offset)
        )

        return target_date.strftime("%m/%d/%Y")

    # =========================================================================
    # PAGE LOAD TESTS
    # =========================================================================

    @pytest.mark.smoke
    def test_find_transactions_page_loads_correctly(self):
        """Verify Find Transactions page loads."""

        self.login_and_navigate()

        assert "ParaBank" in self.page.title()

    @pytest.mark.smoke
    def test_account_dropdown_populates_correctly(self):
        """Verify account dropdown contains accounts."""

        self.login_and_navigate()

        accounts = (
            self.find_transactions_page
            .get_available_accounts()
        )

        assert isinstance(accounts, list)
        assert len(accounts) > 0

    # =========================================================================
    # SEARCH TESTS
    # =========================================================================

    @pytest.mark.smoke
    def test_search_transactions_by_date(self):
        """Verify transaction search by date."""

        self.login_and_navigate()

        accounts = self.find_transactions_page.get_available_accounts()

        assert len(accounts) > 0

        self.find_transactions_page.search_transactions(
            account_id=accounts[0],
            date=self.get_date_string(-30)
        )

        assert self.page.url.endswith("findtrans.htm")



    @pytest.mark.smoke
    def test_search_transactions_by_date_range(self):
        """Verify transaction search by date range."""

        self.login_and_navigate()

        accounts = self.find_transactions_page.get_available_accounts()

        assert len(accounts) > 0

        self.find_transactions_page.search_transactions(
            account_id=accounts[0],
            from_date=self.get_date_string(-30),
            to_date=self.get_date_string()
        )

        assert self.page.url.endswith("findtrans.htm")

    @pytest.mark.smoke
    def test_search_transactions_by_amount(self):
        """Verify transaction search by amount."""

        self.login_and_navigate()

        accounts = self.find_transactions_page.get_available_accounts()

        assert len(accounts) > 0

        self.find_transactions_page.search_transactions(
            account_id=accounts[0],
            amount="100"
        )

        print(self.page.locator("#rightPanel").inner_text())

        # FIX: stabilize UI state (important for this page)
        self.find_transactions_page.wait_for_search_results()

        has_results = self.find_transactions_page.has_transactions()
        no_results_message = self.find_transactions_page.get_no_results_message()

        # FIXED ASSERTION (safe + compatible with your page class)
        assert (
            has_results is True
            or "no transactions" in no_results_message.lower()
        ), (
            f"Search returned invalid state: "
            f"has_results={has_results}, "
            f"message='{no_results_message}'"
        )
    # =========================================================================
    # FORM TESTS
    # =========================================================================

    @pytest.mark.regression
    def test_clear_search_form(self):
        """Verify search form clears successfully."""

        self.login_and_navigate()

        accounts = self.find_transactions_page.get_available_accounts()

        assert len(accounts) > 0

        self.find_transactions_page.select_account(accounts[0])

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
    
    # =========================================================================
# NAVIGATION TESTS
# =========================================================================

    @pytest.mark.navigation
    def test_accounts_overview_link_navigation(self):
        """Verify Accounts Overview navigation."""

        self.login_and_navigate()

        self.find_transactions_page.click_accounts_overview()

        self.accounts_page.assert_accounts_overview_loaded()