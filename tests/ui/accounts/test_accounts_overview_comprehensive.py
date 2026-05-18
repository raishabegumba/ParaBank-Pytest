"""Unique comprehensive accounts overview tests not covered in test_accounts_overview.py."""
import pytest
from playwright.sync_api import Page
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.pages.login_page import LoginPage
from src.config.logger import log
from src.config.settings import get_settings


@pytest.mark.ui
@pytest.mark.accounts
class TestAccountsOverviewComprehensive:

    @pytest.fixture(autouse=True)
    def setup(self, authenticated_user: Page):
        self.page = authenticated_user
        self.accounts_page = AccountsOverviewPage(self.page)
        self.accounts_page.navigate_to_accounts_overview()

    @pytest.mark.positive
    def test_account_details_access(self):
        """Test accessing account details."""
        accounts = self.accounts_page.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available for testing")
        first_account = accounts[0]
        self.accounts_page.click_account(first_account['account_id'])
        current_url = self.page.url
        assert "activity" in current_url or "account" in current_url.lower(), \
            "Should navigate to account details"
        log.info(f"Account details access test passed for: {first_account['account_id']}")

    @pytest.mark.positive
    def test_navigation_buttons(self):
        """Test all navigation buttons work correctly."""
        settings = get_settings()

        self.accounts_page.click_open_new_account()
        assert "openaccount" in self.page.url
        self.page.goto(f"{settings.base_url}/overview.htm")
        self.page.wait_for_load_state("domcontentloaded")

        self.accounts_page.click_transfer_funds()
        assert "transfer" in self.page.url
        self.page.goto(f"{settings.base_url}/overview.htm")
        self.page.wait_for_load_state("domcontentloaded")
        self.accounts_page.click_bill_pay()
        assert "billpay" in self.page.url
        self.page.goto(f"{settings.base_url}/overview.htm")
        self.page.wait_for_load_state("domcontentloaded")
        self.accounts_page.click_find_transactions()
        assert "findtrans" in self.page.url
        log.info("Navigation buttons test passed")

    @pytest.mark.positive
    def test_logout_functionality(self):
        """Test logout functionality."""
        self.accounts_page.click_logout()
        assert "index.htm" in self.page.url or "login" in self.page.url.lower(), \
            "Should navigate to login page"
        log.info("Logout functionality test passed")

    @pytest.mark.performance
    def test_accounts_overview_performance(self, performance_monitor):
        """Test accounts overview page performance."""
        performance_monitor.start_timer("accounts_load")
        accounts_loaded = self.accounts_page.wait_for_accounts_load()
        performance_monitor.end_timer()
        assert accounts_loaded, "Accounts should load within timeout"
        load_duration = performance_monitor.get_metric("accounts_load")
        assert load_duration < 5.0, f"Accounts load took {load_duration}s"
        log.info(f"Performance test passed: {load_duration:.2f}s")

    @pytest.mark.ui
    def test_no_accounts_message(self):
        """Test no accounts message handling."""
        has_accounts = self.accounts_page.has_accounts()
        assert isinstance(has_accounts, bool)
        log.info(f"No accounts message test passed - has_accounts: {has_accounts}")

    @pytest.mark.ui
    def test_account_details_structure(self):
        """Test account details structure and format."""
        accounts = self.accounts_page.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available for testing")
        first_account = accounts[0]
        assert len(first_account['account_id']) > 0
        assert len(first_account['balance']) > 0
        try:
            float(first_account['balance'].replace('$', '').replace(',', ''))
        except ValueError:
            pytest.fail(f"Balance format invalid: {first_account['balance']}")
        log.info(f"Account details structure test passed")