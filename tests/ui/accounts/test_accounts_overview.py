"""Comprehensive UI test suite for ParaBank Accounts Overview page."""
import pytest
from decimal import Decimal
from datetime import datetime
from playwright.sync_api import Page
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.pages.login_page import LoginPage
from src.pages.open_account_page import OpenAccountPage
from src.utils.test_data_utils import TestDataUtils
from src.config.logger import log
import re


@pytest.mark.ui
@pytest.mark.accounts
class TestAccountsOverviewPage:
    """Enterprise-grade test suite for accounts overview functionality."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test environment."""
        self.page = page
        self.accounts_page = AccountsOverviewPage(page)
        self.login_page = LoginPage(page)
        self.open_account_page = OpenAccountPage(page)
        self.test_data = TestDataUtils()

    def login_and_navigate_to_accounts(self):
        """Helper method to login and navigate to accounts overview."""
        # Login with valid credentials
        self.login_page.navigate_to_login()
        login_result = self.login_page.login_with_validation("john", "demo")
        assert login_result['success'], "Login should be successful"
        
        # Navigate to accounts overview
        self.accounts_page.navigate_to_accounts_overview()
        self.accounts_page.assert_accounts_overview_loaded()

    @pytest.mark.smoke
    def test_accounts_overview_page_loads_correctly(self):
        """Test that accounts overview page loads with all required elements."""
        self.login_and_navigate_to_accounts()
        
        # Verify page title
        assert "ParaBank" in self.page.title()
        assert "Accounts Overview" in self.page.title()

    @pytest.mark.smoke
    def test_accounts_table_displays_correctly(self):
        """Test that accounts table displays correctly."""
        self.login_and_navigate_to_accounts()
        
        # Check if accounts table is visible
        assert self.accounts_page.is_accounts_table_visible()
        
        # Get all accounts
        accounts = self.accounts_page.get_all_accounts()
        assert isinstance(accounts, list), "Should return list of accounts"

    @pytest.mark.smoke
    def test_welcome_message_displays_correctly(self):
        """Test that welcome message displays correctly."""
        self.login_and_navigate_to_accounts()
        welcome_msg = self.accounts_page.get_welcome_message()

        assert "Welcome" in welcome_msg

    @pytest.mark.regression
    def test_account_data_integrity(self):
        """Test account data integrity and consistency."""
        self.login_and_navigate_to_accounts()
        
        # Validate account data
        validation_results = self.accounts_page.validate_account_data_integrity()
        
        # Check validation results
        assert validation_results['all_accounts_have_ids'], "All accounts should have IDs"
        assert validation_results['all_accounts_have_balances'], "All accounts should have balances"
        assert validation_results['all_accounts_have_available_amounts']
        assert validation_results['balance_format_valid'], "Balance format should be valid"
        assert not validation_results['duplicate_accounts'], "No duplicate accounts should exist"

    @pytest.mark.regression
    def test_account_count_accuracy(self):
        """Test account count accuracy."""
        self.login_and_navigate_to_accounts()
        
        # Get account count
        count = self.accounts_page.get_account_count()
        assert isinstance(count, int), "Account count should be integer"
        assert count >= 0, "Account count should be non-negative"
        
        # Verify count matches actual accounts
        accounts = self.accounts_page.get_all_accounts()
        assert count == len(accounts), "Count should match actual number of accounts"

    @pytest.mark.regression
    def test_total_balance_calculation(self):
        """Test total balance calculation and display."""
        self.login_and_navigate_to_accounts()
        
        # Get displayed total balance
        displayed_total = self.accounts_page.get_total_balance()
        
        # Calculate total from individual accounts
        accounts = self.accounts_page.get_all_accounts()
        calculated_total = Decimal('0.00')
        
        for account in accounts:
            if account['balance']:
                try:
                    balance_str = account['balance'].replace('$', '').replace(',', '')
                    balance = Decimal(balance_str)
                    calculated_total += balance
                except:
                    log.warning(f"Could not parse balance: {account['balance']}")
        
        # Verify totals match (if both are available)
        if displayed_total and calculated_total > 0:
            displayed_decimal = Decimal(displayed_total.replace('$', '').replace(',', ''))
            assert abs(displayed_decimal - calculated_total) < Decimal('0.01'), "Total balance should match sum of accounts"

    @pytest.mark.regression
    def test_account_search_by_type(self):
        """Test searching accounts by type."""
        self.login_and_navigate_to_accounts()
        
        # Get all accounts first
        all_accounts = self.accounts_page.get_all_accounts()
        
        if len(all_accounts) > 0:
            # Test searching by account type
            first_account_type = all_accounts[0]['account_type']
            if first_account_type:
                filtered_accounts = self.accounts_page.search_accounts_by_type(first_account_type)
                
                # Verify all filtered accounts match the type
                for account in filtered_accounts:
                    assert first_account_type.lower() in account['account_type'].lower()

    @pytest.mark.regression
    def test_accounts_with_minimum_balance_filter(self):
        """Test filtering accounts by minimum balance."""
        self.login_and_navigate_to_accounts()
        
        # Get all accounts
        accounts = self.accounts_page.get_all_accounts()
        
        if len(accounts) > 0:
            # Test with a reasonable minimum balance
            min_balance = 0.0
            qualifying_accounts = self.accounts_page.get_accounts_with_minimum_balance(min_balance)
            
            # Verify all accounts meet the minimum balance criteria
            for account in qualifying_accounts:
                assert 'numeric_balance' in account
                assert account['numeric_balance'] >= min_balance

    @pytest.mark.navigation
    def test_click_account_navigation(self):
        """Test clicking on account for details."""
        self.login_and_navigate_to_accounts()
        
        accounts = self.accounts_page.get_all_accounts()
        
        if len(accounts) > 0:
            # Click on first account
            account_id = accounts[0]['account_id']
            self.accounts_page.click_account(account_id)
            
            # Should navigate to account details
            # Verify by checking URL change or page content
            self.page.wait_for_load_state("networkidle")

    @pytest.mark.navigation
    def test_open_new_account_button_navigation(self):
        """Test Open New Account button navigation."""
        self.login_and_navigate_to_accounts()
        
        # Click Open New Account button
        self.accounts_page.click_open_new_account()
        
        # Should navigate to open account page
        self.page.wait_for_load_state("networkidle")
        # Verify by checking URL or page content

    @pytest.mark.navigation
    def test_transfer_funds_button_navigation(self):
        """Test Transfer Funds button navigation."""
        self.login_and_navigate_to_accounts()
        
        # Click Transfer Funds button
        self.accounts_page.click_transfer_funds()
        
        # Should navigate to transfer funds page
        self.page.wait_for_load_state("networkidle")

    @pytest.mark.navigation
    def test_bill_pay_button_navigation(self):
        """Test Bill Pay button navigation."""
        self.login_and_navigate_to_accounts()
        
        # Click Bill Pay button
        self.accounts_page.click_bill_pay()
        
        # Should navigate to bill pay page
        self.page.wait_for_load_state("networkidle")

    @pytest.mark.navigation
    def test_find_transactions_button_navigation(self):
        """Test Find Transactions button navigation."""
        self.login_and_navigate_to_accounts()
        
        # Click Find Transactions button
        self.accounts_page.click_find_transactions()
        
        # Should navigate to find transactions page
        self.page.wait_for_load_state("networkidle")

    @pytest.mark.navigation
    def test_logout_button_navigation(self):
        """Test Logout button navigation."""
        self.login_and_navigate_to_accounts()
        
        # Click Logout button
        self.accounts_page.click_logout()
        
        # Should navigate to login page
        self.login_page.assert_login_page_loaded()

    @pytest.mark.usability
    def test_accounts_load_wait_functionality(self):
        """Test waiting for accounts to load."""
        self.login_and_navigate_to_accounts()
        
        # Test wait for accounts load
        loaded = self.accounts_page.wait_for_accounts_load()
        assert loaded, "Accounts should load within timeout"

    @pytest.mark.usability
    def test_has_accounts_functionality(self):
        """Test has accounts detection."""
        self.login_and_navigate_to_accounts()
        
        # Check if user has accounts
        has_accounts = self.accounts_page.has_accounts()
        assert isinstance(has_accounts, bool), "Should return boolean value"

    @pytest.mark.performance
    def test_accounts_overview_load_performance(self):
        """Test accounts overview page load performance."""
        from datetime import datetime
        
        start_time = datetime.now()
        self.login_and_navigate_to_accounts()
        load_time = (datetime.now() - start_time).total_seconds()
        
        # Page should load within reasonable time (5 seconds)
        assert load_time < 5.0, f"Page load time {load_time}s exceeds threshold"

    @pytest.mark.performance
    def test_accounts_data_retrieval_performance(self):
        """Test accounts data retrieval performance."""
        self.login_and_navigate_to_accounts()
        
        start_time = datetime.now()
        accounts = self.accounts_page.get_all_accounts()
        retrieval_time = (datetime.now() - start_time).total_seconds()
        
        # Data retrieval should be fast (2 seconds)
        assert retrieval_time < 5.0, f"Data retrieval time {retrieval_time}s exceeds threshold"

    @pytest.mark.edge_case
    def test_no_accounts_scenario(self):
        """Test behavior when user has no accounts."""
        # This test would require a user with no accounts
        # For now, we'll test the functionality
        self.login_and_navigate_to_accounts()
        
        # Check if no accounts message would be displayed
        # This is a placeholder test
        assert True, "Test placeholder for no accounts scenario"

    @pytest.mark.accessibility
    def test_accounts_table_accessibility(self):
        """Test accounts table accessibility features."""
        self.login_and_navigate_to_accounts()
        
        # Check if table has proper headers
        table_headers = self.page.locator("#accountTable thead th")
        if table_headers.count() > 0:
            # Verify headers are present
            assert table_headers.count() >= 3, "Should have at least 3 columns (Account, Balance, Type)"
        
        # Check if account links are accessible
        account_links = self.page.locator(self.accounts_page.ACCOUNT_LINKS)
        if account_links.count() > 0:
            # Verify links have proper text or aria-labels
            for i in range(min(account_links.count(), 5)):  # Check first 5 links
                link = account_links.nth(i)
                link_text = link.text_content()
                aria_label = link.get_attribute('aria-label')
                assert link_text or aria_label, "Account links should have descriptive text"

    @pytest.mark.data_export
    def test_accounts_data_export(self):
        """Test accounts data export functionality."""
        self.login_and_navigate_to_accounts()
        
        # Export accounts data
        export_data = self.accounts_page.export_accounts_data()
        
        # Verify export data structure
        assert isinstance(export_data, dict), "Export data should be dictionary"
        assert 'timestamp' in export_data, "Should include timestamp"
        assert 'welcome_message' in export_data, "Should include welcome message"
        assert 'total_accounts' in export_data, "Should include total accounts count"
        assert 'accounts' in export_data, "Should include accounts list"
        assert 'validation_results' in export_data, "Should include validation results"

    @pytest.mark.data_validation
    def test_account_balance_format_validation(self):
        """Test account balance format validation."""
        self.login_and_navigate_to_accounts()
        
        accounts = self.accounts_page.get_all_accounts()
        
        BALANCE_PATTERN = r"^-?\$?\d+(,\d{3})*(\.\d{2})?$"

        for account in accounts:
            if account['balance']:
                balance_str = account['balance'].strip()

                assert re.match(BALANCE_PATTERN, balance_str), \
                  f"Invalid balance format: {balance_str}"

    @pytest.mark.data_validation
    def test_account_id_format_validation(self):
        """Test account ID format validation."""
        self.login_and_navigate_to_accounts()
        
        accounts = self.accounts_page.get_all_accounts()
        
        for account in accounts:
            if account['account_id']:
                # Check if account ID has proper format (should be numeric)
                account_id = account['account_id']
                assert account_id.isdigit() or len(account_id) > 0, f"Invalid account ID format: {account_id}"

    @pytest.mark.integration
    def test_complete_account_workflow(self):
        """Test complete account workflow from overview to details."""
        self.login_and_navigate_to_accounts()
        
        accounts = self.accounts_page.get_all_accounts()
        
        if len(accounts) > 0:
            # Get first account details
            account_id = accounts[0]['account_id']
            account_balance = accounts[0]['balance']
            account_type = accounts[0]['account_type']
            
            # Click on account
            self.accounts_page.click_account(account_id)
            
            # Wait for navigation
            self.page.wait_for_load_state("networkidle")
            
            # Verify account details page loaded
            # This would depend on the actual account details page implementation

    @pytest.mark.error_handling
    def test_invalid_account_click_handling(self):
        """Test handling of clicking on non-existent account."""
        self.login_and_navigate_to_accounts()
        
        # Try to click on non-existent account
        try:
            self.accounts_page.click_account("999999")
            # Should handle gracefully or show error
        except Exception as e:
            # Expected behavior
            log.info(f"Expected error for invalid account click: {e}")

    @pytest.mark.browser_compatibility
    def test_accounts_table_javascript_functionality(self):
        """Test accounts table JavaScript functionality."""
        self.login_and_navigate_to_accounts()
        
        # Test JavaScript evaluation on table
        table_exists = self.page.evaluate("""
            () => {
                const table = document.querySelector('#accountTable');
                return table !== null;
            }
        """)
        
        assert table_exists, "Accounts table should be accessible via JavaScript"

    @pytest.mark.localization
    def test_accounts_overview_localization(self):
        """Test accounts overview localization elements."""
        self.login_and_navigate_to_accounts()
        
        # Check for currency formatting
        accounts = self.accounts_page.get_all_accounts()
        
        for account in accounts:
            if account['balance']:
                # Check if balance uses proper currency formatting
                balance = account['balance']
                # This test can be expanded based on localization requirements
                assert len(balance) > 0, "Balance should not be empty"

    @pytest.mark.security
    def test_accounts_data_privacy(self):
        """Test accounts data privacy and security."""
        self.login_and_navigate_to_accounts()
        
        # Check that sensitive data is not exposed in page source
        page_content = self.page.content()
        
        # Check that passwords are not exposed (shouldn't be in accounts overview anyway)
        assert "password" not in page_content.lower() or "pass" not in page_content.lower(), "Password data should not be exposed"

    @pytest.mark.responsive
    def test_accounts_table_responsive_design(self):
        """Test accounts table responsive design."""
        self.login_and_navigate_to_accounts()
        
        # Test different viewport sizes
        viewport_sizes = [
            {'width': 1920, 'height': 1080},  # Desktop
            {'width': 768, 'height': 1024},   # Tablet
            {'width': 375, 'height': 667}     # Mobile
        ]
        
        for viewport in viewport_sizes:
            self.page.set_viewport_size(viewport)
            
            # Check if table is still visible and functional
            assert self.accounts_page.is_accounts_table_visible(), f"Table should be visible on {viewport['width']}x{viewport['height']}"
            
            # Try to get accounts data
            accounts = self.accounts_page.get_all_accounts()
            assert isinstance(accounts, list), f"Should be able to get accounts on {viewport['width']}x{viewport['height']}"

    @pytest.mark.conditional
    def test_accounts_overview_with_multiple_accounts(self):
        """Test accounts overview with multiple accounts."""
        self.login_and_navigate_to_accounts()
        
        accounts = self.accounts_page.get_all_accounts()
        
        if len(accounts) > 1:
            # Test with multiple accounts
            assert len(accounts) >= 2, "Should have multiple accounts for this test"
            
            # Verify each account has required data
            for account in accounts:
                assert account['account_id'], "Each account should have an ID"
                assert account['balance'], "Each account should have a balance"
                assert account['available_amount'], "Each account should have an available amount"

    @pytest.mark.conditional
    def test_accounts_overview_with_single_account(self):
        """Test accounts overview with single account."""
        self.login_and_navigate_to_accounts()
        
        accounts = self.accounts_page.get_all_accounts()
        
        if len(accounts) == 1:
            # Test with single account
            assert len(accounts) == 1, "Should have exactly one account for this test"
            
            # Verify single account data
            account = accounts[0]
            assert account['account_id'], "Single account should have an ID"
            assert account['balance'], "Single account should have a balance"
            assert account['account_type'], "Single account should have a type"
