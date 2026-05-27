"""
==============================================================================
Financial Services Workflow Tests
==============================================================================
"""

import pytest
import allure
from playwright.sync_api import Page

from src.pages.accounts_overview_page import AccountsOverviewPage
from src.pages.bill_pay_page import BillPayPage
from src.pages.loan_request_page import LoanRequestPage
from src.config.logger import log


@allure.feature("Workflow Tests")
@allure.story("Financial Services")
class TestFinancialServicesWorkflow:

    @pytest.mark.workflow
    @pytest.mark.e2e
    @allure.title("Bill Payment Workflow")
    def test_bill_payment_workflow(
        self,
        logged_in_page: Page,
        valid_bill_payment_data
    ):
        page = logged_in_page

        accounts_page = AccountsOverviewPage(page)
        billpay_page = BillPayPage(page)

        accounts_page.click_bill_pay()

        billpay_page.assert_bill_pay_page_loaded()

        accounts = billpay_page.get_available_accounts()

        assert len(accounts) > 0

        billpay_page.send_payment(
            from_account=accounts[0],
            amount="75.00",
            payee_info=valid_bill_payment_data
        )

        billpay_page.wait_for_payment_complete()

        assert billpay_page.is_payment_successful()

        log.info("Bill payment workflow completed")

    @pytest.mark.workflow
    @pytest.mark.e2e
    @allure.title("Loan Application Workflow")
    def test_loan_application_workflow(
        self,
        logged_in_page: Page,
        valid_loan_data
    ):
        page = logged_in_page

        loan_page = LoanRequestPage(page)

        loan_page.navigate_to_loan_request()

        loan_page.assert_loan_request_page_loaded()

        accounts = loan_page.get_available_accounts()

        assert len(accounts) > 0

        loan_page.apply_for_loan(
            loan_amount=valid_loan_data["loan_amount"],
            down_payment=valid_loan_data["down_payment"],
            from_account=accounts[0]
        )

        assert loan_page.wait_for_loan_processing_complete()

        details = loan_page.get_loan_result_details()

        assert details["status"] != ""

        log.info("Loan application workflow completed")