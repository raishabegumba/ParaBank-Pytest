"""Parallel execution transfer funds tests."""
import pytest
from playwright.sync_api import Page
from src.pages.transfer_funds_page import TransferFundsPage
from src.pages.login_page import LoginPage
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.transfer
@pytest.mark.parallel
class TestTransferFundsParallel:

    def test_parallel_transfer_performance(self, page: Page):
        """Test transfer performance under parallel execution."""
        from datetime import datetime

        login_page = LoginPage(page)
        login_page.navigate_to_login()
        login_page.login_with_validation("john", "demo")

        transfer_page = TransferFundsPage(page)
        transfer_page.navigate_to_transfer_funds()

        from_accounts = transfer_page.get_from_accounts()
        to_accounts = transfer_page.get_to_accounts()

        if len(from_accounts) < 2:
            pytest.skip("Need at least 2 accounts")

        from_account = from_accounts[0]
        to_account = [acc for acc in to_accounts if acc != from_account][0]

        start = datetime.now()
        transfer_page.perform_transfer(from_account, to_account, "50.00")
        transfer_complete = transfer_page.wait_for_transfer_complete()
        duration = (datetime.now() - start).total_seconds()

        assert transfer_complete, "Parallel transfer should complete"
        assert duration < 10.0, f"Parallel transfer took {duration}s"
        log.info(f"Parallel transfer performance passed: {duration:.2f}s")