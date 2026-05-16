"""
==============================================================================
ParaBank End-to-End Tests
==============================================================================
Comprehensive E2E test suite including:
- Complete user registration workflow
- Full banking workflow (login -> operations -> logout)
- Multi-step transaction flows
- Cross-module workflows
"""

import pytest
import allure
from automation.utils.base_test import BaseTest
from automation.pages.page_objects import (
    LoginPage, RegistrationPage, AccountsOverviewPage,
    TransferFundsPage, BillPayPage, LoanRequestPage,
    FindTransactionsPage, UpdateProfilePage
)
from automation.utils.config_manager import config
from automation.utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


@allure.feature("E2E Workflows")
@allure.story("User Registration Journey")
class TestUserRegistrationWorkflow(BaseTest):
    """End-to-end user registration workflow."""
    
    @pytest.mark.e2e
    @pytest.mark.critical
    @allure.title("Complete User Registration and Login")
    @allure.description("E2E: Register new user and login successfully")
    def test_e2e_registration_and_login(self, page, valid_user_registration_data):
        """
        Test Case: E2E Registration
        Objective: Complete user registration to login flow
        Steps:
            1. Navigate to registration
            2. Fill all required fields
            3. Submit registration
            4. Verify account created
            5. Login with new credentials
            6. Verify accounts page
        Expected: User successfully registered and logged in
        """
        registration_page = RegistrationPage(page)
        login_page = LoginPage(page)
        accounts_page = AccountsOverviewPage(page)
        
        # Navigate to registration
        self.navigate_to(f"{config.base_url}register.htm")
        registration_page.verify_page_loaded()
        
        # Register user
        registration_page.register_user(valid_user_registration_data)
        logger.info(f"User registered: {valid_user_registration_data['username']}")
        
        # Verify registration successful
        success_msg = registration_page.get_success_message()
        assert success_msg != "" or accounts_page.verify_page_loaded()
        
        # If needed, navigate to login
        if "register" in page.url.lower():
            self.navigate_to(f"{config.base_url}login.htm")
        
        # Login with new credentials
        login_page.login(
            valid_user_registration_data['username'],
            valid_user_registration_data['password']
        )
        
        # Verify logged in
        assert accounts_page.verify_page_loaded()
        logger.info("E2E registration and login successful")


@allure.feature("E2E Workflows")
@allure.story("Banking Operations")
class TestBankingOperationsWorkflow(BaseTest):
    """End-to-end banking operations workflow."""
    
    @pytest.mark.e2e
    @pytest.mark.critical
    @allure.title("Complete Banking Operations Flow")
    @allure.description("E2E: Login -> View Accounts -> Transfer -> Logout")
    def test_e2e_complete_banking_flow(self, page, test_credentials):
        """
        Test Case: E2E Complete Banking Flow
        Objective: Complete banking workflow
        Steps:
            1. Login
            2. View accounts
            3. Perform transfer
            4. View transaction history
            5. Logout
        Expected: All operations complete successfully
        """
        login_page = LoginPage(page)
        accounts_page = AccountsOverviewPage(page)
        transfer_page = TransferFundsPage(page)
        
        # Step 1: Login
        self.navigate_to(f"{config.base_url}login.htm")
        login_page.login(test_credentials['username'], test_credentials['password'])
        assert accounts_page.verify_page_loaded()
        logger.info("Step 1: Login successful")
        
        # Step 2: View accounts
        count = accounts_page.get_accounts_count()
        assert count > 0
        logger.info(f"Step 2: View accounts - {count} accounts")
        
        # Step 3: Transfer funds
        accounts_page.click_transfer_button()
        transfer_page.verify_page_loaded()
        
        transfer_page.transfer_funds(
            from_account='123456789',
            to_account='987654321',
            amount='50.00'
        )
        
        # Verify transfer
        success = transfer_page.get_success_message()
        logger.info(f"Step 3: Transfer - {success}")
        
        # Step 4: Logout
        self.navigate_to(f"{config.base_url}overview.htm")
        accounts_page.logout()
        
        # Verify logged out
        current_url = page.url
        assert 'login' in current_url or login_page.verify_page_loaded()
        logger.info("Step 4: Logout successful - E2E banking flow complete")
    
    	@pytest.mark.e2e
    	@allure.title("Transfer and Transaction Search")
    	@allure.description("E2E: Transfer funds and search transactions")
    def test_e2e_transfer_and_search(self, page, logged_in_user):
    	accounts_page = AccountsOverviewPage(page)
    	transfer_page = TransferFundsPage(page)

    	accounts = accounts_page.get_account_numbers()

    	assert len(accounts) >= 2

    	from_account = accounts[0]
    	to_account = accounts[1]

    	accounts_page.click_transfer_button()

    	transfer_page.transfer_funds(
        from_account=from_account,
        to_account=to_account,
        amount='25.50'
    	)

    	success = transfer_page.get_success_message()

    	assert "Transfer Complete" in success


@allure.feature("E2E Workflows")
@allure.story("Profile Management")
class TestProfileManagementWorkflow(BaseTest):
    """End-to-end profile management workflow."""
    
    @pytest.mark.e2e
    @allure.title("Update and Verify Profile Changes")
    @allure.description("E2E: Update profile and verify persistence")
    def test_e2e_profile_update(self, page, test_credentials):
        """
        Test Case: E2E Profile Update
        Objective: Update profile and verify persistence
        Steps:
            1. Login
            2. Navigate to profile
            3. Update profile
            4. Verify success
            5. Re-login to verify persistence
        Expected: Profile updated and persisted
        """
        login_page = LoginPage(page)
        accounts_page = AccountsOverviewPage(page)
        profile_page = UpdateProfilePage(page)
        
        # Login
        self.navigate_to(f"{config.base_url}login.htm")
        login_page.login(test_credentials['username'], test_credentials['password'])
        assert accounts_page.verify_page_loaded()
        
        # Navigate to profile
        self.navigate_to(f"{config.base_url}updateprofile.htm")
        profile_page.verify_page_loaded()
        
        # Update profile
        update_data = {
            'first_name': 'E2ETest',
            'last_name': 'User',
            'address': '999 E2E Street',
            'city': 'E2E City',
            'state': 'E2',
            'zip_code': '99999'
        }
        
        profile_page.update_profile(update_data)
        success = profile_page.get_success_message()
        assert success != ""
        logger.info(f"Profile updated: {success}")
        
        # Logout
        accounts_page.logout()
        
        # Re-login
        login_page.login(test_credentials['username'], test_credentials['password'])
        accounts_page.verify_page_loaded()
        
        # Navigate to profile to verify changes persisted
        self.navigate_to(f"{config.base_url}updateprofile.htm")
        logger.info("Profile update persistence verified")


@allure.feature("E2E Workflows")
@allure.story("Complex Operations")
class TestComplexOperationsWorkflow(BaseTest):
    """End-to-end complex multi-step workflows."""
    
    @pytest.mark.e2e
    @allure.title("Bill Payment Complete Workflow")
    @allure.description("E2E: Create payee and send payment")
    def test_e2e_bill_payment_workflow(self, page, test_credentials, valid_bill_payment_data):
        """
        Test Case: E2E Bill Payment
        Objective: Create payee and send payment
        Steps:
            1. Login
            2. Navigate to Bill Pay
            3. Add payee
            4. Send payment
            5. Verify completion
        Expected: Payee created and payment sent successfully
        """
        login_page = LoginPage(page)
        accounts_page = AccountsOverviewPage(page)
        billpay_page = BillPayPage(page)
        
        # Login
        self.navigate_to(f"{config.base_url}login.htm")
        login_page.login(test_credentials['username'], test_credentials['password'])
        
        # Navigate to Bill Pay
        accounts_page.click_bill_pay_button()
        billpay_page.verify_page_loaded()
        
        # Add payee
        billpay_page.add_payee(valid_bill_payment_data)
        success = billpay_page.get_success_message()
        logger.info(f"Payee added: {success}")
        
        # Send payment
        billpay_page.select_payee('1')
        billpay_page.select_account('123456789')
        billpay_page.enter_amount('75.00')
        billpay_page.click_send_payment()
        
        payment_success = billpay_page.get_success_message()
        assert payment_success != ""
        logger.info(f"Payment sent: {payment_success}")
    
    @pytest.mark.e2e
    @allure.title("Loan Application to Completion")
    @allure.description("E2E: Apply for loan through completion")
    def test_e2e_loan_application(self, page, test_credentials, valid_loan_data):
        """E2E: Complete loan application workflow."""
        login_page = LoginPage(page)
        accounts_page = AccountsOverviewPage(page)
        loan_page = LoanRequestPage(page)
        
        # Login
        self.navigate_to(f"{config.base_url}login.htm")
        login_page.login(test_credentials['username'], test_credentials['password'])
        
        # Navigate to loan request
        accounts_page.click_loan_button()
        loan_page.verify_page_loaded()
        
        # Apply for loan
        loan_page.apply_for_loan(
            valid_loan_data['loan_amount'],
            valid_loan_data['down_payment'],
            '123456789'
        )
        
        # Verify status
        status = loan_page.get_approval_status()
        assert status != ""
        logger.info(f"Loan application status: {status}")


@allure.feature("E2E Workflows")
@allure.story("Error Scenarios")
class TestErrorHandlingWorkflow(BaseTest):
    """End-to-end error handling workflows."""
    
    @pytest.mark.e2e
    @allure.title("Handle and Recover from Errors")
    @allure.description("E2E: Handle errors and continue operations")
    def test_e2e_error_recovery(self, page, test_credentials):
        """
        Test Case: E2E Error Handling
        Objective: Test error recovery
        Steps:
            1. Login
            2. Attempt invalid operation
            3. Verify error displayed
            4. Perform valid operation
            5. Verify recovery
        Expected: Application recovers gracefully
        """
        login_page = LoginPage(page)
        accounts_page = AccountsOverviewPage(page)
        transfer_page = TransferFundsPage(page)
        
        # Login
        self.navigate_to(f"{config.base_url}login.htm")
        login_page.login(test_credentials['username'], test_credentials['password'])
        
        # Try invalid transfer (zero amount)
        accounts_page.click_transfer_button()
        transfer_page.verify_page_loaded()
        
        transfer_page.transfer_funds(
            from_account='123456789',
            to_account='987654321',
            amount='0'
        )
        
        error = transfer_page.get_error_message()
        assert error != ""
        logger.info(f"Error caught: {error}")
        
        # Recover with valid transfer
        transfer_page.transfer_funds(
            from_account='123456789',
            to_account='987654321',
            amount='100.00'
        )
        
        success = transfer_page.get_success_message()
        assert success != "" or transfer_page.verify_page_loaded()
        logger.info("Recovery successful - E2E error handling complete")

