"""Parallel execution accounts overview tests."""
import pytest
from playwright.sync_api import Page
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.accounts
@pytest.mark.parallel
class TestAccountsOverviewParallel:

    def test_parallel_accounts_load(self, page: Page):
        """Test accounts overview loading under parallel execution."""
        from src.pages.login_page import LoginPage
        login_page = LoginPage(page)
        login_page.navigate_to_login()
        login_page.login_with_validation("john", "demo")

        accounts_page = AccountsOverviewPage(page)
        accounts_page.navigate_to_accounts_overview()
        accounts_loaded = accounts_page.wait_for_accounts_load()
        assert accounts_loaded, "Parallel accounts load should complete"
        log.info("Parallel accounts load test passed")