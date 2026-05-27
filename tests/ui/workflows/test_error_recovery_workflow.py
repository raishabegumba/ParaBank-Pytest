"""
==============================================================================
Error Recovery Workflow Tests
==============================================================================
"""

import pytest
import allure
from playwright.sync_api import Page

from src.pages.login_page import LoginPage
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.pages.transfer_funds_page import TransferFundsPage
from src.config.settings import get_settings
from src.config.logger import log

settings = get_settings()


@allure.feature("Workflow Tests")
@allure.story("Error Recovery")
class TestErrorRecoveryWorkflow:

    @pytest.mark.workflow
    @pytest.mark.e2e
    @allure.title("Transfer Error Recovery Workflow")
    def test_transfer_error_recovery_workflow(
        self,
        logged_in_page: Page
    ):
        page = logged_in_page

        transfer_page = TransferFundsPage(page)

        page.goto(f"{settings.base_url}/transfer.htm")

        from_accounts = transfer_page.get_from_accounts()
        to_accounts = transfer_page.get_to_accounts()

        from_account = from_accounts[0]
        to_account = next(
            (a for a in to_accounts if a != from_account),
            to_accounts[-1]
        )

        # Invalid transfer
        try:
            transfer_page.perform_transfer(
                from_account=from_account,
                to_account=to_account,
                amount="0"
            )
        except ValueError:
            log.info("Validation error handled successfully")

        # Recovery
        transfer_page.perform_transfer(
            from_account=from_account,
            to_account=to_account,
            amount="10.00"
        )

        assert transfer_page.is_transfer_successful()

        log.info("Transfer recovery workflow completed")

    @pytest.mark.workflow
    @pytest.mark.e2e
    @allure.title("Login Error Recovery Workflow")
    def test_login_error_recovery_workflow(
        self,
        page: Page,
        test_credentials
    ):
        login_page = LoginPage(page)
        accounts_page = AccountsOverviewPage(page)

        login_page.navigate_to_login()

        login_page.enter_username(
            test_credentials["username"]
        )

        login_page.enter_password(
            "WrongPassword999!"
        )

        login_page.click_login()

        page.wait_for_load_state("networkidle")

        assert (
            login_page.is_error_message_displayed()
            or not accounts_page.verify_page_loaded()
        )

        # Recovery login
        login_page.login(
            test_credentials["username"],
            test_credentials["password"]
        )

        page.wait_for_load_state("networkidle")

        assert accounts_page.verify_page_loaded()

        log.info("Login recovery workflow completed")