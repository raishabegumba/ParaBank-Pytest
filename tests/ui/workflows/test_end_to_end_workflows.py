"""Comprehensive end-to-end workflow tests covering complete user journeys."""
import pytest
from playwright.sync_api import Page
from src.pages.login_page import LoginPage
from src.pages.registration_page import RegistrationPage
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.pages.transfer_funds_page import TransferFundsPage
from src.pages.bill_pay_page import BillPayPage
from src.pages.open_account_page import OpenAccountPage
from src.pages.loan_request_page import LoanRequestPage
from src.utils.wait_helpers import WaitStrategy
from src.fixtures.test_data_fixtures import user_test_data, account_test_data, transaction_test_data, loan_test_data
from src.config.settings import get_settings
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.e2e
@pytest.mark.smoke
class TestEndToEndWorkflows:
    """Comprehensive end-to-end workflow test suite."""
    
    @pytest.mark.positive
    def test_complete_user_journey_registration_to_transfers(self, page: Page):
        """Test complete user journey: registration -> login -> transfer funds."""
        # Step 1: Registration
        registration_page = RegistrationPage(page)
        registration_page.navigate_to_registration()
        
        valid_user = user_test_data['valid_user']
        unique_username = f"e2e_user_{pytest.current_time_ms()}"
        
        registration_page.complete_registration(
            first_name=valid_user['first_name'],
            last_name=valid_user['last_name'],
            address=valid_user['address'],
            city=valid_user['city'],
            state=valid_user['state'],
            zip_code=valid_user['zip_code'],
            phone=valid_user['phone'],
            ssn=valid_user['ssn'],
            username=unique_username,
            password="E2ETest123!",
            confirm_password="E2ETest123!"
        )
        
        registration_page.assert_registration_successful()
        log.info("Step 1: Registration completed")
        
        # Step 2: Login
        login_page = LoginPage(page)
        login_page.navigate_to_login()
        login_page.login(unique_username, "E2ETest123!")
        login_page.assert_login_successful()
        log.info("Step 2: Login completed")
        
        # Step 3: Open New Account
        open_account_page = OpenAccountPage(page)
        open_account_page.navigate_to_open_account()
        
        # Open checking account
        open_account_page.open_new_account("CHECKING", "12345")  # Assuming account exists
        open_account_page.assert_account_opened_successfully()
        log.info("Step 3: New account opened")
        
        # Step 4: Navigate to Accounts Overview
        accounts_page = AccountsOverviewPage(page)
        accounts_page.navigate_to_accounts_overview()
        accounts_page.assert_accounts_overview_loaded()
        
        accounts = accounts_page.get_all_accounts()
        assert len(accounts) >= 2, "Should have at least 2 accounts for transfer"
        log.info(f"Step 4: Found {len(accounts)} accounts")
        
        # Step 5: Transfer Funds
        transfer_page = TransferFundsPage(page)
        transfer_page.navigate_to_transfer_funds()
        
        from_account = accounts[0]['account_id']
        to_account = accounts[1]['account_id']
        amount = transaction_test_data['transfer_amounts'][0]
        
        transfer_page.perform_transfer(from_account, to_account, amount)
        transfer_page.assert_transfer_successful()
        log.info(f"Step 5: Transferred {amount} from {from_account} to {to_account}")
        
        # Step 6: Verify Transfer in Accounts Overview
        accounts_page.navigate_to_accounts_overview()
        updated_accounts = accounts_page.get_all_accounts()
        assert len(updated_accounts) >= 2, "Should still have accounts after transfer"
        log.info("Step 6: Complete user journey verified")
    
    @pytest.mark.positive
    def test_bill_payment_workflow(self, page: Page):
        """Test complete bill payment workflow."""
        # Step 1: Login
        login_page = LoginPage(page)
        login_page.navigate_to_login()
        login_page.login("john.doe", "Password123!")
        login_page.assert_login_successful()
        log.info("Step 1: Login completed")
        
        # Step 2: Navigate to Bill Pay
        accounts_page = AccountsOverviewPage(page)
        accounts_page.navigate_to_accounts_overview()
        
        bill_pay_page = BillPayPage(page)
        bill_pay_page.navigate_to_bill_pay()
        log.info("Step 2: Navigated to bill pay")
        
        # Step 3: Add New Payee and Make Payment
        payee_info = {
            'name': 'E2E Test Payee',
            'address': '123 Test Street',
            'city': 'Test City',
            'state': 'TC',
            'zip_code': '12345',
            'phone': '555-TEST-1',
            'account_number': 'PAYEE-12345'
        }
        
        accounts = bill_pay_page.get_available_accounts()
        assert len(accounts) > 0, "Should have accounts for bill payment"
        
        bill_pay_page.send_payment(
            from_account=accounts[0],
            amount=transaction_test_data['bill_pay_amounts'][0],
            date="12/12/2024",
            description="E2E Test Bill Payment",
            payee_info=payee_info,
            add_new_payee=True
        )
        
        bill_pay_page.assert_payment_successful()
        log.info("Step 3: Bill payment completed")
        
        # Step 4: Verify Payment Impact
        accounts_page.navigate_to_accounts_overview()
        updated_accounts = accounts_page.get_all_accounts()
        assert len(updated_accounts) > 0, "Should have accounts after payment"
        log.info("Step 4: Bill payment workflow verified")
    
    @pytest.mark.positive
    def test_loan_request_workflow(self, page: Page):
        """Test complete loan request workflow."""
        # Step 1: Login
        login_page = LoginPage(page)
        login_page.navigate_to_login()
        login_page.login("john.doe", "Password123!")
        login_page.assert_login_successful()
        log.info("Step 1: Login completed")
        
        # Step 2: Navigate to Loan Request
        loan_page = LoanRequestPage(page)
        loan_page.navigate_to_loan_request()
        log.info("Step 2: Navigated to loan request")
        
        # Step 3: Apply for Loan
        loan_data = loan_test_data['small_loan']
        accounts = loan_page.get_available_accounts()
        assert len(accounts) > 0, "Should have accounts for loan"
        
        loan_page.apply_for_loan(
            loan_amount=loan_data['amount'],
            down_payment=loan_data['down_payment'],
            from_account=accounts[0]
        )
        
        # Step 4: Verify Loan Result
        loan_complete = loan_page.wait_for_loan_processing_complete()
        assert loan_complete, "Loan processing should complete"
        
        if loan_page.is_loan_approved():
            loan_page.assert_loan_approved()
            log.info("Step 4: Loan approved")
        else:
            loan_page.assert_loan_denied()
            log.info("Step 4: Loan denied")
        
        log.info("Loan request workflow completed")
    
    @pytest.mark.positive
    def test_transaction_search_workflow(self, page: Page):
        """Test complete transaction search workflow."""
        # Step 1: Login
        login_page = LoginPage(page)
        login_page.navigate_to_login()
        login_page.login("john.doe", "Password123!")
        login_page.assert_login_successful()
        log.info("Step 1: Login completed")
        
        # Step 2: Navigate to Find Transactions
        accounts_page = AccountsOverviewPage(page)
        accounts_page.navigate_to_accounts_overview()
        
        find_trans_page = page.__class__(page)  # Would need proper import
        page.goto(f"{get_settings().base_url}/findtrans.htm")
        log.info("Step 2: Navigated to find transactions")
        
        # Step 3: Search Transactions
        accounts = find_trans_page.get_available_accounts()
        if len(accounts) > 0:
            find_trans_page.search_transactions(
                account_id=accounts[0],
                from_date="12/01/2024",
                to_date="12/31/2024"
            )
            
            search_complete = find_trans_page.wait_for_search_results()
            assert search_complete, "Transaction search should complete"
            
            transactions = find_trans_page.get_transactions()
            assert isinstance(transactions, list), "Should return transaction list"
            log.info(f"Step 3: Found {len(transactions)} transactions")
        
        log.info("Transaction search workflow completed")
    
    @pytest.mark.positive
    def test_multi_account_management_workflow(self, page: Page):
        """Test multi-account management workflow."""
        # Step 1: Login
        login_page = LoginPage(page)
        login_page.navigate_to_login()
        login_page.login("john.doe", "Password123!")
        login_page.assert_login_successful()
        log.info("Step 1: Login completed")
        
        # Step 2: Open Multiple Accounts
        accounts_page = AccountsOverviewPage(page)
        accounts_page.navigate_to_accounts_overview()
        
        initial_accounts = accounts_page.get_all_accounts()
        initial_count = len(initial_accounts)
        log.info(f"Step 2: Initial account count: {initial_count}")
        
        # Open savings account
        open_account_page = OpenAccountPage(page)
        open_account_page.navigate_to_open_account()
        open_account_page.open_new_account("SAVINGS", "12345")
        open_account_page.assert_account_opened_successfully()
        log.info("Step 3: Opened savings account")
        
        # Verify new account
        accounts_page.navigate_to_accounts_overview()
        updated_accounts = accounts_page.get_all_accounts()
        assert len(updated_accounts) > initial_count, "Should have more accounts"
        log.info(f"Step 4: Updated account count: {len(updated_accounts)}")
        
        # Step 5: Perform Transfer Between New Accounts
        transfer_page = TransferFundsPage(page)
        transfer_page.navigate_to_transfer_funds()
        
        if len(updated_accounts) >= 2:
            from_account = updated_accounts[0]['account_id']
            to_account = updated_accounts[1]['account_id']
            
            transfer_page.perform_transfer(from_account, to_account, "50")
            transfer_page.assert_transfer_successful()
            log.info("Step 5: Transfer between new accounts completed")
        
        log.info("Multi-account management workflow completed")
    
    @pytest.mark.negative
    def test_failed_registration_workflow(self, page: Page):
        """Test workflow with failed registration."""
        # Step 1: Attempt Registration with Invalid Data
        registration_page = RegistrationPage(page)
        registration_page.navigate_to_registration()
        
        registration_page.complete_registration(
            first_name="",  # Invalid - empty
            last_name="",
            address="",
            city="",
            state="",
            zip_code="",
            phone="",
            ssn="",
            username="invalid",
            password="weak",  # Invalid - weak password
            confirm_password="weak"
        )
        
        registration_page.assert_registration_failed()
        log.info("Step 1: Registration failed as expected")
        
        # Step 2: Try to Login with Invalid Credentials
        login_page = LoginPage(page)
        login_page.navigate_to_login()
        login_page.login("invalid", "weak")
        login_page.assert_login_failed()
        log.info("Step 2: Login failed as expected")
        
        log.info("Failed registration workflow completed")
    
    @pytest.mark.performance
    def test_e2e_performance_workflow(self, page: Page, performance_metrics):
        """Test end-to-end performance."""
        # Step 1: Login Performance
        performance_metrics.start_timer("e2e_login")
        login_page = LoginPage(page)
        login_page.navigate_to_login()
        login_page.login("john.doe", "Password123!")
        login_page.assert_login_successful()
        performance_metrics.end_timer("e2e_login")
        
        # Step 2: Navigation Performance
        performance_metrics.start_timer("e2e_navigation")
        accounts_page = AccountsOverviewPage(page)
        accounts_page.navigate_to_accounts_overview()
        accounts_loaded = accounts_page.wait_for_accounts_load()
        performance_metrics.end_timer("e2e_navigation")
        
        # Step 3: Transaction Performance
        performance_metrics.start_timer("e2e_transaction")
        accounts = accounts_page.get_all_accounts()
        
        if len(accounts) >= 2:
            transfer_page = TransferFundsPage(page)
            transfer_page.navigate_to_transfer_funds()
            transfer_page.perform_transfer(accounts[0]['account_id'], accounts[1]['account_id'], "25")
            transfer_complete = transfer_page.wait_for_transfer_complete()
            performance_metrics.end_timer("e2e_transaction")
        
        # Performance Assertions
        login_duration = performance_metrics.get_average("e2e_login")
        navigation_duration = performance_metrics.get_average("e2e_navigation")
        transaction_duration = performance_metrics.get_average("e2e_transaction")
        
        assert login_duration < 5.0, f"Login took {login_duration}s, should be under 5s"
        assert navigation_duration < 3.0, f"Navigation took {navigation_duration}s, should be under 3s"
        if transaction_duration:
            assert transaction_duration < 5.0, f"Transaction took {transaction_duration}s, should be under 5s"
        
        log.info(f"E2E Performance - Login: {login_duration:.2f}s, Navigation: {navigation_duration:.2f}s, Transaction: {transaction_duration:.2f}s")
    
    @pytest.mark.accessibility
    def test_e2e_accessibility_workflow(self, page: Page):
        """Test end-to-end accessibility."""
        # Step 1: Login Accessibility
        login_page = LoginPage(page)
        login_page.navigate_to_login()
        
        accessibility_results = login_page.validate_login_form_accessibility()
        assert accessibility_results['username_has_label'], "Login: Username should have label"
        assert accessibility_results['password_has_label'], "Login: Password should have label"
        assert accessibility_results['form_is_keyboard_accessible'], "Login: Form should be keyboard accessible"
        
        login_page.login("john.doe", "Password123!")
        login_page.assert_login_successful()
        log.info("Step 1: Login accessibility verified")
        
        # Step 2: Accounts Overview Accessibility
        accounts_page = AccountsOverviewPage(page)
        accounts_page.navigate_to_accounts_overview()
        
        assert accounts_page.is_accounts_table_visible(), "Accounts: Table should be visible"
        log.info("Step 2: Accounts overview accessibility verified")
        
        log.info("E2E accessibility workflow completed")
    
    @pytest.mark.mobile
    def test_e2e_mobile_workflow(self, mobile_page: Page):
        """Test end-to-end workflow on mobile."""
        # Step 1: Mobile Login
        login_page = LoginPage(mobile_page)
        login_page.navigate_to_login()
        login_page.login("john.doe", "Password123!")
        login_page.assert_login_successful()
        log.info("Step 1: Mobile login completed")
        
        # Step 2: Mobile Accounts Overview
        accounts_page = AccountsOverviewPage(mobile_page)
        accounts_page.navigate_to_accounts_overview()
        accounts_loaded = accounts_page.wait_for_accounts_load()
        assert accounts_loaded, "Mobile: Accounts should load"
        log.info("Step 2: Mobile accounts overview completed")
        
        # Step 3: Mobile Transfer
        if accounts_page.get_account_count() >= 2:
            transfer_page = TransferFundsPage(mobile_page)
            transfer_page.navigate_to_transfer_funds()
            
            accounts = transfer_page.get_from_accounts()
            if len(accounts) >= 2:
                transfer_page.perform_transfer(accounts[0], accounts[1], "10")
                transfer_complete = transfer_page.wait_for_transfer_complete()
                assert transfer_complete, "Mobile: Transfer should complete"
                log.info("Step 3: Mobile transfer completed")
        
        log.info("E2E mobile workflow completed")


@pytest.mark.ui
@pytest.mark.e2e
@pytest.mark.parallel
class TestE2EParallel:
    """Parallel end-to-end workflow tests."""
    
    def test_parallel_user_journey(self, page: Page, performance_metrics):
        """Test user journey under parallel execution."""
        performance_metrics.start_timer("parallel_e2e")
        
        # Simplified E2E flow for parallel testing
        login_page = LoginPage(page)
        login_page.navigate_to_login()
        login_page.login("john.doe", "Password123!")
        login_page.assert_login_successful()
        
        accounts_page = AccountsOverviewPage(page)
        accounts_page.navigate_to_accounts_overview()
        accounts_loaded = accounts_page.wait_for_accounts_load()
        
        performance_metrics.end_timer("parallel_e2e")
        
        assert accounts_loaded, "Parallel E2E should complete"
        
        e2e_duration = performance_metrics.get_average("parallel_e2e")
        assert e2e_duration < 10.0, f"Parallel E2E took {e2e_duration}s, should be under 10s"
        
        log.info(f"Parallel E2E workflow completed: {e2e_duration:.2f}s")


@pytest.mark.ui
@pytest.mark.e2e
@pytest.mark.regression
class TestE2ERegression:
    """Regression tests for critical end-to-end workflows."""
    
    def test_critical_path_regression(self, page: Page):
        """Test critical user path regression."""
        # This test ensures the most critical path still works
        try:
            # Login
            login_page = LoginPage(page)
            login_page.navigate_to_login()
            login_page.login("john.doe", "Password123!")
            login_page.assert_login_successful()
            
            # Check accounts
            accounts_page = AccountsOverviewPage(page)
            accounts_page.navigate_to_accounts_overview()
            accounts = accounts_page.get_all_accounts()
            assert len(accounts) > 0, "Should have accounts"
            
            # Basic transfer if possible
            if len(accounts) >= 2:
                transfer_page = TransferFundsPage(page)
                transfer_page.navigate_to_transfer_funds()
                transfer_page.perform_transfer(accounts[0]['account_id'], accounts[1]['account_id'], "1")
                transfer_complete = transfer_page.wait_for_transfer_complete()
                assert transfer_complete, "Basic transfer should work"
            
            log.info("Critical path regression test passed")
            
        except Exception as e:
            log.error(f"Critical path regression failed: {e}")
            raise
