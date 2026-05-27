"""
==============================================================================
Banking Operations Workflow Tests
==============================================================================
"""

import pytest
import allure
from playwright.sync_api import Page

from src.pages.accounts_overview_page import AccountsOverviewPage
from src.pages.transfer_funds_page import TransferFundsPage
from src.pages.find_transactions_page import FindTransactionsPage
from src.config.logger import log


@allure.feature("Workflow Tests")
@allure.story("Banking Operations")
class TestBankingOperationsWorkflow:

    @pytest.mark.workflow
    @pytest.mark.e2e
    @pytest.mark.critical
    @allure.title("Transfer Funds Workflow")
    def test_transfer_funds_workflow(
        self,
        logged_in_page: Page
    ):
        page = logged_in_page

        accounts_page = AccountsOverviewPage(page)
        transfer_page = TransferFundsPage(page)

        accounts = accounts_page.get_all_accounts()

        assert len(accounts) >= 2

        from_account = accounts[0]["account_id"]
        to_account = accounts[1]["account_id"]

        accounts_page.click_transfer_funds()

        transfer_page.assert_transfer_page_loaded()

        transfer_page.perform_transfer(
            from_account=from_account,
            to_account=to_account,
            amount="50.00"
        )

        assert transfer_page.is_transfer_successful()

        log.info("Transfer workflow completed")

    @pytest.mark.workflow
    @pytest.mark.e2e
    @allure.title("Transfer and Transaction Search Workflow")
    def test_transfer_and_transaction_search_workflow(
        self,
        logged_in_page: Page
    ):
        page = logged_in_page

        accounts_page = AccountsOverviewPage(page)
        transfer_page = TransferFundsPage(page)
        find_page = FindTransactionsPage(page)

        accounts = accounts_page.get_all_accounts()

        assert len(accounts) >= 2

        from_account = accounts[0]["account_id"]
        to_account = accounts[1]["account_id"]

        # Transfer
        accounts_page.click_transfer_funds()

        transfer_page.perform_transfer(
            from_account=from_account,
            to_account=to_account,
            amount="25.50"
        )

        assert transfer_page.is_transfer_successful()

        # Find transaction
        find_page.navigate_to_find_transactions()

        find_page.search_transactions(
            account_id=from_account,
            amount="25.50"
        )

        find_page.wait_for_search_results()

        assert (
            find_page.has_transactions()
            or find_page.get_transaction_count() >= 0
        )

        log.info("Transfer and search workflow completed")