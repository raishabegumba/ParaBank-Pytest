"""Comprehensive accounts overview page tests covering all scenarios."""
import pytest
from playwright.sync_api import Page
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.pages.login_page import LoginPage
from src.utils.wait_helpers import WaitStrategy
from src.fixtures.test_data_fixtures import user_test_data, account_test_data
from src.config.settings import get_settings
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.accounts
@pytest.mark.smoke
class TestAccountsOverviewComprehensive:
    """Comprehensive accounts overview test suite."""
    
    @pytest.fixture(autouse=True)
    def setup(self, authenticated_user: Page):

        """Setup authenticated test instance."""
        self.page = authenticated_page
        self.accounts_page = AccountsOverviewPage(self.page)
        self.accounts_page.navigate_to_accounts_overview()
    
    @pytest.mark.positive
    def test_accounts_overview_loaded(self):
        """Test accounts overview page loads correctly."""
        # Assert
        self.accounts_page.assert_accounts_overview_loaded()
        
        log.info("Accounts overview load test passed")
    
    @pytest.mark.positive
    def test_accounts_table_display(self):
        """Test accounts table displays correctly."""
        # Act
        accounts = self.accounts_page.get_all_accounts()
        
        # Assert
        assert isinstance(accounts, list), "Should return list of accounts"
        
        if accounts:
            # Check account structure
            first_account = accounts[0]
            required_keys = ['account_id', 'balance', 'account_type']
            assert all(key in first_account for key in required_keys), "Account should have required fields"
        
        log.info(f"Accounts table display test passed - found {len(accounts)} accounts")
    
    @pytest.mark.positive
    def test_account_details_access(self):
        """Test accessing account details."""
        # Arrange
        accounts = self.accounts_page.get_all_accounts()
        
        if not accounts:
            pytest.skip("No accounts available for testing")
        
        first_account = accounts[0]
        
        # Act
        self.accounts_page.click_account(first_account['account_id'])
        
        # Assert
        current_url = self.accounts_page.get_url()
        assert "account" in current_url.lower() or "details" in current_url.lower(), \
            "Should navigate to account details"
        
        log.info(f"Account details access test passed for: {first_account['account_id']}")
    
    @pytest.mark.positive
    def test_navigation_buttons(self):
        """Test all navigation buttons work correctly."""
        # Test Open New Account
        self.accounts_page.click_open_new_account()
        current_url = self.accounts_page.get_url()
        assert "openaccount" in current_url, "Should navigate to open account"
        
        # Navigate back
        self.accounts_page.navigate_to_accounts_overview()
        
        # Test Transfer Funds
        self.accounts_page.click_transfer_funds()
        current_url = self.accounts_page.get_url()
        assert "transfer" in current_url, "Should navigate to transfer funds"
        
        # Navigate back
        self.accounts_page.navigate_to_accounts_overview()
        
        # Test Bill Pay
        self.accounts_page.click_bill_pay()
        current_url = self.accounts_page.get_url()
        assert "billpay" in current_url, "Should navigate to bill pay"
        
        # Navigate back
        self.accounts_page.navigate_to_accounts_overview()
        
        # Test Find Transactions
        self.accounts_page.click_find_transactions()
        current_url = self.accounts_page.get_url()
        assert "findtrans" in current_url, "Should navigate to find transactions"
        
        log.info("Navigation buttons test passed")
    
    @pytest.mark.positive
    def test_logout_functionality(self):
        """Test logout functionality."""
        # Act
        self.accounts_page.click_logout()
        
        # Assert
        current_url = self.accounts_page.get_url()
        assert "index.htm" in current_url or "login" in current_url, \
            "Should navigate to login page"
        
        log.info("Logout functionality test passed")
    
    @pytest.mark.positive
    def test_welcome_message_display(self):
        """Test welcome message is displayed."""
        # Act
        welcome_message = self.accounts_page.get_welcome_message()
        
        # Assert
        assert len(welcome_message) > 0, "Welcome message should be displayed"
        assert "Welcome" in welcome_message, "Should contain Welcome"
        
        log.info(f"Welcome message test passed: {welcome_message}")
    
    @pytest.mark.positive
    def test_total_balance_display(self):
        """Test total balance is displayed correctly."""
        # Act
        total_balance = self.accounts_page.get_total_balance()
        account_count = self.accounts_page.get_account_count()
        
        # Assert
        if account_count > 0:
            assert len(total_balance) > 0, "Total balance should be displayed when accounts exist"
            assert "$" in total_balance, "Balance should contain currency symbol"
        
        log.info(f"Total balance test passed: {total_balance}")
    
    @pytest.mark.positive
    def test_account_search_by_type(self):
        """Test searching accounts by type."""
        # Arrange
        accounts = self.accounts_page.get_all_accounts()
        
        if not accounts:
            pytest.skip("No accounts available for testing")
        
        # Act
        checking_accounts = self.accounts_page.search_accounts_by_type("Checking")
        savings_accounts = self.accounts_page.search_accounts_by_type("Savings")
        
        # Assert
        assert isinstance(checking_accounts, list), "Should return list of checking accounts"
        assert isinstance(savings_accounts, list), "Should return list of savings accounts"
        
        # Verify filtering works
        for account in checking_accounts:
            assert "checking" in account['account_type'].lower(), \
                "Checking accounts should have checking type"
        
        for account in savings_accounts:
            assert "savings" in account['account_type'].lower(), \
                "Savings accounts should have savings type"
        
        log.info("Account search by type test passed")
    
    @pytest.mark.positive
    def test_account_balance_filtering(self):
        """Test filtering accounts by minimum balance."""
        # Arrange
        accounts = self.accounts_page.get_all_accounts()
        
        if not accounts:
            pytest.skip("No accounts available for testing")
        
        # Act
        high_balance_accounts = self.accounts_page.get_accounts_with_minimum_balance(1000)
        
        # Assert
        assert isinstance(high_balance_accounts, list), "Should return list of accounts"
        
        # Verify filtering works
        for account in high_balance_accounts:
            balance_str = account['balance'].replace('$', '').replace(',', '')
            balance = float(balance_str)
            assert balance >= 1000, "All accounts should meet minimum balance criteria"
        
        log.info(f"Account balance filtering test passed - found {len(high_balance_accounts)} accounts")
    
    @pytest.mark.data_integrity
    def test_account_data_integrity(self):
        """Test account data integrity and consistency."""
        # Act
        validation_results = self.accounts_page.validate_account_data_integrity()
        
        # Assert
        assert isinstance(validation_results, dict), "Should return validation results dictionary"
        
        # Check critical validations
        assert validation_results['all_accounts_have_ids'], "All accounts should have IDs"
        assert validation_results['all_accounts_have_balances'], "All accounts should have balances"
        assert validation_results['all_accounts_have_types'], "All accounts should have types"
        assert not validation_results['duplicate_accounts'], "Should not have duplicate accounts"
        
        log.info("Account data integrity test passed")
    
    @pytest.mark.performance
    def test_accounts_overview_performance(self, performance_metrics):
        """Test accounts overview page performance."""
        # Act
        performance_metrics.start_timer("accounts_load")
        accounts_loaded = self.accounts_page.wait_for_accounts_load()
        performance_metrics.end_timer("accounts_load")
        
        # Assert
        assert accounts_loaded, "Accounts should load within timeout"
        
        # Check performance
        load_duration = performance_metrics.get_average("accounts_load")
        assert load_duration < 5.0, f"Accounts load took {load_duration}s, should be under 5s"
        
        log.info(f"Accounts overview performance test passed: {load_duration:.2f}s")
    
    @pytest.mark.ui
    def test_no_accounts_message(self):
        """Test no accounts message when appropriate."""
        # This test would need a user with no accounts
        # For now, just verify the method exists and works
        has_accounts = self.accounts_page.has_accounts()
        no_accounts_message = self.accounts_page.get_no_accounts_message()
        
        # Assert
        assert isinstance(has_accounts, bool), "Should return boolean"
        assert isinstance(no_accounts_message, str), "Should return string"
        
        log.info(f"No accounts message test passed - has_accounts: {has_accounts}")
    
    @pytest.mark.ui
    def test_accounts_data_export(self):
        """Test exporting accounts data."""
        # Act
        export_data = self.accounts_page.export_accounts_data()
        
        # Assert
        assert isinstance(export_data, dict), "Should return export data dictionary"
        
        # Check required export fields
        required_fields = ['timestamp', 'welcome_message', 'total_accounts', 'accounts']
        assert all(field in export_data for field in required_fields), \
            "Export should contain required fields"
        
        # Check data structure
        assert isinstance(export_data['accounts'], list), "Accounts should be a list"
        assert isinstance(export_data['total_accounts'], int), "Total should be integer"
        
        log.info(f"Accounts data export test passed - exported {export_data['total_accounts']} accounts")
    
    @pytest.mark.accessibility
    def test_accounts_overview_accessibility(self):
        """Test accounts overview page accessibility."""
        # Act
        accounts = self.accounts_page.get_all_accounts()
        
        # Assert - Basic accessibility checks
        assert self.accounts_page.is_accounts_table_visible(), "Accounts table should be visible"
        
        if accounts:
            # Check that table has proper structure
            account_count = self.accounts_page.get_account_count()
            assert account_count > 0, "Should have at least one account"
        
        log.info("Accounts overview accessibility test passed")
    
    @pytest.mark.regression
    def test_accounts_overview_refresh(self):
        """Test refreshing accounts overview page."""
        # Arrange
        initial_accounts = self.accounts_page.get_all_accounts()
        initial_count = len(initial_accounts)
        
        # Act
        self.accounts_page.refresh_page()
        
        # Wait for page to reload
        self.accounts_page.wait_for_accounts_load()
        
        # Assert
        refreshed_accounts = self.accounts_page.get_all_accounts()
        refreshed_count = len(refreshed_accounts)
        
        assert refreshed_count == initial_count, \
            f"Account count should match after refresh: {initial_count} vs {refreshed_count}"
        
        log.info("Accounts overview refresh test passed")
    
    @pytest.mark.ui
    def test_account_details_structure(self):
        """Test account details structure and format."""
        # Arrange
        accounts = self.accounts_page.get_all_accounts()
        
        if not accounts:
            pytest.skip("No accounts available for testing")
        
        # Act
        first_account = accounts[0]
        
        # Assert
        # Check account ID format
        account_id = first_account['account_id']
        assert len(account_id) > 0, "Account ID should not be empty"
        
        # Check balance format
        balance = first_account['balance']
        assert len(balance) > 0, "Balance should not be empty"
        
        # Try to parse balance
        try:
            balance_value = float(balance.replace('$', '').replace(',', ''))
            assert isinstance(balance_value, (int, float)), "Balance should be numeric"
        except ValueError:
            pytest.fail(f"Balance format is invalid: {balance}")
        
        # Check account type
        account_type = first_account['account_type']
        assert len(account_type) > 0, "Account type should not be empty"
        assert account_type in ['Checking', 'Savings', 'Credit Card', 'Loan'], \
            f"Account type should be valid: {account_type}"
        
        log.info(f"Account details structure test passed for: {account_id}")


@pytest.mark.ui
@pytest.mark.accounts
@pytest.mark.parallel
class TestAccountsOverviewParallel:
    """Parallel accounts overview tests for performance testing."""
    
    def test_parallel_accounts_load(self, authenticated_page: Page, performance_metrics):
        """Test accounts overview loading under parallel execution."""
        # Setup
        accounts_page = AccountsOverviewPage(authenticated_page)
        accounts_page.navigate_to_accounts_overview()
        
        # Act
        performance_metrics.start_timer("parallel_accounts_load")
        accounts_loaded = accounts_page.wait_for_accounts_load()
        performance_metrics.end_timer("parallel_accounts_load")
        
        # Assert
        assert accounts_loaded, "Parallel accounts load should complete"
        
        log.info("Parallel accounts load test passed")


@pytest.mark.ui
@pytest.mark.accounts
@pytest.mark.mobile
class TestAccountsOverviewMobile:
    """Mobile-specific accounts overview tests."""
    
    def test_mobile_accounts_responsive(self, mobile_page: Page):
        """Test accounts overview on mobile viewport."""
        # Setup
        accounts_page = AccountsOverviewPage(mobile_page)
        
        # Login on mobile
        login_page = LoginPage(mobile_page)
        login_page.navigate_to_login()
        login_page.login("john.doe", "Password123!")
        
        # Navigate to accounts overview
        accounts_page.navigate_to_accounts_overview()
        
        # Assert
        accounts_loaded = accounts_page.wait_for_accounts_load()
        assert accounts_loaded, "Mobile accounts should load"
        
        # Check responsive behavior
        is_table_visible = accounts_page.is_accounts_table_visible()
        assert is_table_visible, "Accounts table should be visible on mobile"
        
        log.info("Mobile accounts overview test passed")
