"""Mobile and responsive tests for Find Transactions page."""

import pytest
from playwright.sync_api import Page

from src.pages.find_transactions_page import FindTransactionsPage
from src.pages.login_page import LoginPage


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
        self.login_page.navigate_to_login()

        login_result = self.login_page.login_with_validation(
            "john",
            "demo"
        )

        assert login_result["success"]

        self.find_transactions_page.navigate_to_find_transactions()

    @pytest.mark.mobile
    def test_find_transactions_mobile_view(self):
        self.page.set_viewport_size({
            "width": 375,
            "height": 667
        })

        self.login_and_navigate()

        assert self.page.is_visible(
            self.find_transactions_page.ACCOUNT_SELECT
        )

        assert self.page.is_visible(
            self.find_transactions_page.FIND_TRANSACTIONS_BUTTON
        )

    @pytest.mark.mobile
    def test_find_transactions_tablet_view(self):
        self.page.set_viewport_size({
            "width": 768,
            "height": 1024
        })

        self.login_and_navigate()

        assert self.page.is_visible(
            self.find_transactions_page.ACCOUNT_SELECT
        )

    @pytest.mark.responsive
    def test_find_transactions_responsive_layout(self):
        self.login_and_navigate()

        viewport_sizes = [
            {"width": 1920, "height": 1080},
            {"width": 768, "height": 1024},
            {"width": 375, "height": 667},
        ]

        for viewport in viewport_sizes:

            self.page.set_viewport_size(viewport)

            assert self.page.is_visible(
                self.find_transactions_page.ACCOUNT_SELECT
            )

            assert self.page.is_visible(
                self.find_transactions_page.TRANSACTION_TYPE_SELECT
            )

            assert self.page.is_visible(
                self.find_transactions_page.FIND_TRANSACTIONS_BUTTON
            )

    @pytest.mark.mobile
    def test_mobile_search_transactions(self):
        self.page.set_viewport_size({
            "width": 375,
            "height": 667
        })

        self.login_and_navigate()

        accounts = (
            self.find_transactions_page.get_available_accounts()
        )

        self.find_transactions_page.search_transactions(
            account_id=accounts[0]
        )

        assert self.find_transactions_page.wait_for_search_results()