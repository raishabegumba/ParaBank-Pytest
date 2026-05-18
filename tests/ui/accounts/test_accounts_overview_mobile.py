"""Mobile viewport accounts overview tests."""
import pytest
from playwright.sync_api import Page
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.pages.login_page import LoginPage
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.accounts
@pytest.mark.mobile
class TestAccountsOverviewMobile:

    def test_mobile_accounts_responsive(self, page: Page):
        """Test accounts overview on mobile viewport."""
        page.set_viewport_size({"width": 375, "height": 667})

        login_page = LoginPage(page)
        login_page.navigate_to_login()
        login_page.login_with_validation("john", "demo")

        accounts_page = AccountsOverviewPage(page)
        accounts_page.navigate_to_accounts_overview()

        assert accounts_page.wait_for_accounts_load(), "Mobile accounts should load"
        assert accounts_page.is_accounts_table_visible(), \
            "Accounts table should be visible on mobile"
        log.info("Mobile accounts overview test passed")