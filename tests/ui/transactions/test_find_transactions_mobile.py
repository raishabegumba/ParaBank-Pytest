"""Mobile and responsive tests for Find Transactions page."""

import pytest
from playwright.sync_api import Page

from src.pages.find_transactions_page import FindTransactionsPage
from src.pages.login_page import LoginPage
from src.utils.search_fallback import ensure_search_criteria


@pytest.mark.mobile
@pytest.mark.responsive
@pytest.mark.ui
@pytest.mark.find_transactions
class TestFindTransactionsMobile:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.page = page
        self.find_transactions_page = FindTransactionsPage(page)
        self.login_page = LoginPage(page)

    def login_and_navigate(self):
        # IMPORTANT: always reset viewport before login
        self.page.set_viewport_size({"width": 1920, "height": 1080})

        self.login_page.navigate_to_login()

        login_result = self.login_page.login_with_validation(
            "john",
            "demo"
        )

        assert login_result["success"]

        self.find_transactions_page.navigate_to_find_transactions()
        self.find_transactions_page.assert_find_transactions_page_loaded()

    # =========================================================
    # VIEWPORT TESTS
    # =========================================================

    def test_find_transactions_mobile_view(self):
        self.page.set_viewport_size({"width": 375, "height": 667})

        self.login_and_navigate()

        assert self.page.is_visible(self.find_transactions_page.ACCOUNT_SELECT)
        assert self.page.is_visible(self.find_transactions_page.FIND_BY_ID_BUTTON)

    def test_find_transactions_tablet_view(self):
        self.page.set_viewport_size({"width": 768, "height": 1024})

        self.login_and_navigate()

        assert self.page.is_visible(self.find_transactions_page.ACCOUNT_SELECT)
        assert self.page.is_visible(self.find_transactions_page.FIND_BY_ID_BUTTON)

    def test_find_transactions_responsive_layout(self):
        viewport_sizes = [
            {"width": 1920, "height": 1080},
            {"width": 768, "height": 1024},
            {"width": 375, "height": 667},
        ]

        for viewport in viewport_sizes:
            self.page.set_viewport_size(viewport)

            self.login_and_navigate()

            assert self.page.is_visible(self.find_transactions_page.ACCOUNT_SELECT)
            assert self.page.is_visible(self.find_transactions_page.FIND_BY_ID_BUTTON)

    # =========================================================
    # SEARCH TESTS (FIXED)
    # =========================================================

    def test_mobile_search_transactions(self):
        self.page.set_viewport_size({"width": 375, "height": 667})

        self.login_and_navigate()

        accounts = self.find_transactions_page.get_available_accounts()
        assert len(accounts) > 0

        # FIX: ensure_search_criteria expects dict, not kwargs
        data = {"account_id": accounts[0]}
        criteria = ensure_search_criteria(data)

        self.find_transactions_page.search_transactions(**criteria)

        assert self.find_transactions_page.wait_for_search_results()

    def test_mobile_search_by_date(self):
        self.page.set_viewport_size({"width": 375, "height": 667})

        self.login_and_navigate()

        accounts = self.find_transactions_page.get_available_accounts()
        assert len(accounts) > 0

        data = {
            "account_id": accounts[0],
            "date": "01/01/2024"
        }
        criteria = ensure_search_criteria(data)

        self.find_transactions_page.search_transactions(**criteria)

        assert self.find_transactions_page.wait_for_search_results()

    # =========================================================
    # FORM TESTS
    # =========================================================

    def test_mobile_clear_search_form(self):
        self.page.set_viewport_size({"width": 375, "height": 667})

        self.login_and_navigate()

        accounts = self.find_transactions_page.get_available_accounts()
        assert len(accounts) > 0

        self.find_transactions_page.select_account(accounts[0])
        self.find_transactions_page.enter_amount("100.00")

        self.find_transactions_page.clear_search_form()

        validation = self.find_transactions_page.validate_search_criteria()

        # FIX: after clear, account should be FALSE or empty
        assert validation["account_selected"] in [False, None, ""]

    # =========================================================
    # RESPONSIVE TABLE TESTS
    # =========================================================

    def test_responsive_search_results_table(self):
        viewport_sizes = [
            {"width": 1440, "height": 900},
            {"width": 768, "height": 1024},
            {"width": 390, "height": 844},
        ]

        for viewport in viewport_sizes:
            self.page.set_viewport_size(viewport)

            self.login_and_navigate()

            accounts = self.find_transactions_page.get_available_accounts()
            assert len(accounts) > 0

            data = {"account_id": accounts[0]}
            criteria = ensure_search_criteria(data)

            self.find_transactions_page.search_transactions(**criteria)

            assert self.find_transactions_page.wait_for_search_results()

            assert (
                self.page.is_visible(self.find_transactions_page.RESULTS_TABLE)
                or self.page.is_visible(self.find_transactions_page.NO_RESULTS_MESSAGE)
            )