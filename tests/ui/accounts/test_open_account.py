import pytest
import time
from src.pages.open_account_page import OpenAccountPage
from src.pages.login_page import LoginPage
from src.pages.accounts_overview_page import AccountsOverviewPage


@pytest.mark.ui
@pytest.mark.open_account
class TestOpenAccountPage:

    @pytest.fixture(autouse=True)
    def setup(self, page):
        self.page = page
        self.open_account_page = OpenAccountPage(page)
        self.login_page = LoginPage(page)
        self.accounts_page = AccountsOverviewPage(page)

    # ---------------- HELPERS ----------------

    def login_and_navigate(self):
        self.login_page.navigate_to_login()
        result = self.login_page.login_with_validation("john", "demo")
        assert result["success"]

        self.open_account_page.navigate_to_open_account()
        self.open_account_page.assert_open_account_page_loaded()

    def require_data(self):
        types = self.open_account_page.get_account_types()
        accounts = self.open_account_page.get_source_accounts()

        if not types or not accounts:
            pytest.skip("No account data available")

        return types, accounts

    # ---------------- TESTS ----------------

    def test_page_load(self):
        self.login_and_navigate()
        assert "ParaBank" in self.page.title()

    def test_dropdowns(self):
        self.login_and_navigate()

        types = self.open_account_page.get_account_types()
        accounts = self.open_account_page.get_source_accounts()

        assert len(types) > 0
        assert len(accounts) > 0

    def test_open_checking_account(self):
        self.login_and_navigate()
        types, accounts = self.require_data()

        checking = next((t for t in types if "CHECKING" in t.upper()), None)
        assert checking is not None

        result = self.open_account_page.simulate_account_opening_with_validation(
            checking,
            accounts[0]
        )

        assert result["success"], result.get("error_message")

    def test_open_savings_account(self):
        self.login_and_navigate()
        types, accounts = self.require_data()

        savings = next((t for t in types if "SAVINGS" in t.upper()), None)
        assert savings is not None

        result = self.open_account_page.simulate_account_opening_with_validation(
            savings,
            accounts[0]
        )

        assert result["success"], result.get("error_message")

    def test_navigation_to_accounts_overview(self):
        self.login_and_navigate()

        self.page.click("#leftPanel a[href*='overview']")
        self.accounts_page.assert_accounts_overview_loaded()

    def test_performance(self):
        self.login_and_navigate()

        start = time.monotonic()
        self.open_account_page.get_account_types()
        self.open_account_page.get_source_accounts()
        duration = time.monotonic() - start

        assert duration < 2.5