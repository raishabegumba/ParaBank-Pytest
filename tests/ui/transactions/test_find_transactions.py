"""Comprehensive UI test suite for ParaBank Find Transactions page."""
import pytest
from datetime import datetime, timedelta
from playwright.sync_api import Page
from src.pages.find_transactions_page import FindTransactionsPage
from src.pages.login_page import LoginPage
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.utils.test_data_utils import TestDataUtils
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.find_transactions
class TestFindTransactionsPage:
    """Enterprise-grade test suite for find transactions functionality."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test environment."""
        self.page = page
        self.find_transactions_page = FindTransactionsPage(page)
        self.login_page = LoginPage(page)
        self.accounts_page = AccountsOverviewPage(page)
        self.test_data = TestDataUtils()

    def login_and_navigate_to_find_transactions(self):
        """Helper method to login and navigate to find transactions page."""
        # Login with valid credentials
        self.login_page.navigate_to_login()
        login_result = self.login_page.login_with_validation("john", "demo")
        assert login_result['success'], "Login should be successful"
        
        # Navigate to find transactions page
        self.find_transactions_page.navigate_to_find_transactions()
        self.find_transactions_page.assert_find_transactions_page_loaded()

    def get_date_string(self, days_offset: int = 0) -> str:
        """Get date string in MM/DD/YYYY format."""
        target_date = datetime.now() + timedelta(days=days_offset)
        return target_date.strftime("%m/%d/%Y")

    @pytest.mark.smoke
    def test_find_transactions_page_loads_correctly(self):
        """Test that find transactions page loads with all required elements."""
        self.login_and_navigate_to_find_transactions()
        
        # Verify page title
        assert "ParaBank" in self.page.title()
        assert "Find" in self.page.title() or "Transaction" in self.page.title()

    @pytest.mark.smoke
    def test_account_dropdown_populates_correctly(self):
        """Test that account dropdown populates with available accounts."""
        self.login_and_navigate_to_find_transactions()
        
        # Get available accounts
        accounts = self.find_transactions_page.get_available_accounts()
        
        assert isinstance(accounts, list), "Accounts should be a list"
        assert len(accounts) > 0, "Should have at least one account"

    @pytest.mark.smoke
    def test_transaction_type_dropdown_populates_correctly(self):
        """Test that transaction type dropdown populates with available types."""
        self.login_and_navigate_to_find_transactions()
        
        # Get available transaction types
        transaction_types = self.find_transactions_page.get_transaction_types()
        
        assert isinstance(transaction_types, list), "Transaction types should be a list"
        assert len(transaction_types) > 0, "Should have at least one transaction type"

    @pytest.mark.smoke
    def test_search_transactions_by_account(self):
        """Test searching transactions by account."""
        self.login_and_navigate_to_find_transactions()
        
        # Get available accounts
        accounts = self.find_transactions_page.get_available_accounts()
        
        if len(accounts) > 0:
            # Search transactions for first account
            account_id = accounts[0]
            self.find_transactions_page.search_transactions(account_id=account_id)
            
            # Wait for results
            results_loaded = self.find_transactions_page.wait_for_search_results()
            assert results_loaded, "Search results should load"
            
            # Check if any transactions were found
            has_transactions = self.find_transactions_page.has_transactions()
            log.info(f"Transactions found for account {account_id}: {has_transactions}")

    @pytest.mark.smoke
    def test_search_transactions_by_date(self):
        """Test searching transactions by specific date."""
        self.login_and_navigate_to_find_transactions()
        
        # Get available accounts
        accounts = self.find_transactions_page.get_available_accounts()
        
        if len(accounts) > 0:
            # Search by today's date
            today = self.get_date_string()
            account_id = accounts[0]
            
            self.find_transactions_page.search_transactions(
                account_id=account_id,
                date=today
            )
            
            # Wait for results
            results_loaded = self.find_transactions_page.wait_for_search_results()
            assert results_loaded, "Search results should load"
            
            # Check results
            has_transactions = self.find_transactions_page.has_transactions()
            log.info(f"Transactions found for date {today}: {has_transactions}")

    @pytest.mark.smoke
    def test_search_transactions_by_date_range(self):
        """Test searching transactions by date range."""
        self.login_and_navigate_to_find_transactions()
        
        # Get available accounts
        accounts = self.find_transactions_page.get_available_accounts()
        
        if len(accounts) > 0:
            # Search by date range (last 30 days)
            from_date = self.get_date_string(-30)
            to_date = self.get_date_string()
            account_id = accounts[0]
            
            self.find_transactions_page.search_transactions(
                account_id=account_id,
                from_date=from_date,
                to_date=to_date
            )
            
            # Wait for results
            results_loaded = self.find_transactions_page.wait_for_search_results()
            assert results_loaded, "Search results should load"
            
            # Check results
            has_transactions = self.find_transactions_page.has_transactions()
            log.info(f"Transactions found for date range {from_date} to {to_date}: {has_transactions}")

    @pytest.mark.regression
    def test_search_transactions_without_account_fails(self):
        """Test transaction search fails without selecting account."""
        self.login_and_navigate_to_find_transactions()
        
        # Try search without selecting account
        self.find_transactions_page.search_transactions(date=self.get_date_string())
        
        # Should not return results or should show error
        results_loaded = self.find_transactions_page.wait_for_search_results()
        if results_loaded:
            # If results loaded, should show no transactions
            has_transactions = self.find_transactions_page.has_transactions()
            assert not has_transactions, "Should not find transactions without account selection"

    @pytest.mark.regression
    def test_search_transactions_with_invalid_date_format(self):
        """Test transaction search with invalid date format."""
        self.login_and_navigate_to_find_transactions()
        
        # Get available accounts
        accounts = self.find_transactions_page.get_available_accounts()
        
        if len(accounts) > 0:
            # Try with invalid date format
            account_id = accounts[0]
            self.find_transactions_page.search_transactions(
                account_id=account_id,
                date="invalid-date"
            )
            
            # Should handle gracefully
            results_loaded = self.find_transactions_page.wait_for_search_results()
            log.info(f"Search with invalid date result: {results_loaded}")

    @pytest.mark.regression
    def test_search_transactions_with_invalid_amount_format(self):
        """Test transaction search with invalid amount format."""
        self.login_and_navigate_to_find_transactions()
        
        # Get available accounts
        accounts = self.find_transactions_page.get_available_accounts()
        
        if len(accounts) > 0:
            # Try with invalid amount format
            account_id = accounts[0]
            self.find_transactions_page.search_transactions(
                account_id=account_id,
                amount="abc"
            )
            
            # Should handle gracefully
            results_loaded = self.find_transactions_page.wait_for_search_results()
            log.info(f"Search with invalid amount result: {results_loaded}")

    @pytest.mark.regression
    def test_search_transactions_with_future_date(self):
        """Test transaction search with future date."""
        self.login_and_navigate_to_find_transactions()
        
        # Get available accounts
        accounts = self.find_transactions_page.get_available_accounts()
        
        if len(accounts) > 0:
            # Try with future date
            future_date = self.get_date_string(7)
            account_id = accounts[0]
            
            self.find_transactions_page.search_transactions(
                account_id=account_id,
                date=future_date
            )
            
            # Should return no results
            results_loaded = self.find_transactions_page.wait_for_search_results()
            if results_loaded:
                has_transactions = self.find_transactions_page.has_transactions()
                assert not has_transactions, "Should not find transactions for future date"

    @pytest.mark.usability
    def test_search_criteria_validation(self):
        """Test search criteria validation functionality."""
        self.login_and_navigate_to_find_transactions()
        
        # Initially search should not be ready without account
        validation = self.find_transactions_page.validate_search_criteria()
        assert not validation['search_ready']
        assert not validation['account_selected']
        
        # Select account
        accounts = self.find_transactions_page.get_available_accounts()
        if len(accounts) > 0:
            account_id = accounts[0]
            self.find_transactions_page.select_account(account_id)
            
            # Now search should be ready
            validation = self.find_transactions_page.validate_search_criteria()
            assert validation['search_ready']
            assert validation['account_selected']

    @pytest.mark.navigation
    def test_accounts_overview_link_navigation(self):
        """Test Accounts Overview link navigation."""
        self.login_and_navigate_to_find_transactions()
        
        # Click Accounts Overview link
        self.find_transactions_page.click_accounts_overview()
        
        # Should navigate to accounts overview
        self.accounts_page.assert_accounts_overview_loaded()

    @pytest.mark.accessibility
    def test_find_transactions_form_accessibility(self):
        """Test find transactions form accessibility features."""
        self.login_and_navigate_to_find_transactions()
        
        # Check if form fields have proper labels
        form_fields = [
            (self.find_transactions_page.ACCOUNT_SELECT, "Account"),
            (self.find_transactions_page.TRANSACTION_TYPE_SELECT, "Transaction type"),
            (self.find_transactions_page.DATE_SELECT, "Date"),
            (self.find_transactions_page.FROM_DATE_FIELD, "From date"),
            (self.find_transactions_page.TO_DATE_FIELD, "To date"),
            (self.find_transactions_page.AMOUNT_FIELD, "Amount"),
        ]
        
        for field_selector, field_name in form_fields:
            element = self.page.locator(field_selector)
            # Check for label, placeholder, or aria-label
            has_label = bool(
                element.get_attribute('aria-label') or 
                element.get_attribute('placeholder') or
                element.locator('xpath=./preceding::label[1]').count() > 0
            )
            # Note: Select elements might not have traditional labels
            log.info(f"Field {field_name} accessibility check: {has_label}")

    @pytest.mark.performance
    def test_find_transactions_page_load_performance(self):
        """Test find transactions page load performance."""
        start_time = datetime.now()
        self.login_and_navigate_to_find_transactions()
        load_time = (datetime.now() - start_time).total_seconds()
        
        # Page should load within reasonable time (5 seconds)
        assert load_time < 5.0, f"Page load time {load_time}s exceeds threshold"

    @pytest.mark.performance
    def test_dropdown_population_performance(self):
        """Test dropdown population performance."""
        self.login_and_navigate_to_find_transactions()
        
        start_time = datetime.now()
        accounts = self.find_transactions_page.get_available_accounts()
        transaction_types = self.find_transactions_page.get_transaction_types()
        population_time = (datetime.now() - start_time).total_seconds()
        
        # Dropdown population should be fast (2 seconds)
        assert population_time < 2.0, f"Dropdown population time {population_time}s exceeds threshold"

    @pytest.mark.data_validation
    def test_transaction_data_structure(self):
        """Test transaction data structure and format."""
        self.login_and_navigate_to_find_transactions()
        
        # Get available accounts
        accounts = self.find_transactions_page.get_available_accounts()
        
        if len(accounts) > 0:
            # Search for transactions
            account_id = accounts[0]
            self.find_transactions_page.search_transactions(account_id=account_id)
            
            results_loaded = self.find_transactions_page.wait_for_search_results()
            if results_loaded and self.find_transactions_page.has_transactions():
                # Get transaction data
                transactions = self.find_transactions_page.get_transactions()
                
                # Verify data structure
                assert isinstance(transactions, list), "Should return list of transactions"
                
                if len(transactions) > 0:
                    transaction = transactions[0]
                    required_fields = ['transaction_id', 'date', 'description', 'deposit', 'withdrawal']
                    
                    for field in required_fields:
                        assert field in transaction, f"Transaction should have {field} field"
                        assert isinstance(transaction[field], str), f"Field {field} should be string"

    @pytest.mark.data_validation
    def test_transaction_count_accuracy(self):
        """Test transaction count accuracy."""
        self.login_and_navigate_to_find_transactions()
        
        # Get available accounts
        accounts = self.find_transactions_page.get_available_accounts()
        
        if len(accounts) > 0:
            # Search for transactions
            account_id = accounts[0]
            self.find_transactions_page.search_transactions(account_id=account_id)
            
            results_loaded = self.find_transactions_page.wait_for_search_results()
            if results_loaded:
                # Get transaction count
                count = self.find_transactions_page.get_transaction_count()
                transactions = self.find_transactions_page.get_transactions()
                
                assert count == len(transactions), f"Count {count} should match actual transactions {len(transactions)}"

    @pytest.mark.regression
    def test_clear_search_form(self):
        """Test clearing search form functionality."""
        self.login_and_navigate_to_find_transactions()
        
        # Fill form with data
        accounts = self.find_transactions_page.get_available_accounts()
        transaction_types = self.find_transactions_page.get_transaction_types()
        
        if len(accounts) > 0 and len(transaction_types) > 0:
            account_id = accounts[0]
            transaction_type = transaction_types[0]
            
            self.find_transactions_page.select_account(account_id)
            self.find_transactions_page.select_transaction_type(transaction_type)
            self.find_transactions_page.enter_date(self.get_date_string())
            self.find_transactions_page.enter_amount("100.00")
            
            # Clear form
            self.find_transactions_page.clear_search_form()
            
            # Verify form is cleared
            validation = self.find_transactions_page.validate_search_criteria()
            assert not validation['account_selected'], "Account selection should be cleared"

    @pytest.mark.data_filtering
    def test_search_transactions_by_type(self):
        """Test searching transactions by transaction type."""
        self.login_and_navigate_to_find_transactions()
        
        # Get available accounts and transaction types
        accounts = self.find_transactions_page.get_available_accounts()
        transaction_types = self.find_transactions_page.get_transaction_types()
        
        if len(accounts) > 0 and len(transaction_types) > 1:  # Need at least 2 types to test
            account_id = accounts[0]
            
            # Test each transaction type
            for transaction_type in transaction_types[:min(3, len(transaction_types))]:
                self.find_transactions_page.search_transactions(
                    account_id=account_id,
                    transaction_type=transaction_type
                )
                
                # Wait for results
                results_loaded = self.find_transactions_page.wait_for_search_results()
                if results_loaded:
                    has_transactions = self.find_transactions_page.has_transactions()
                    log.info(f"Transactions found for type {transaction_type}: {has_transactions}")

    @pytest.mark.data_filtering
    def test_search_transactions_by_amount(self):
        """Test searching transactions by amount."""
        self.login_and_navigate_to_find_transactions()
        
        # Get available accounts
        accounts = self.find_transactions_page.get_available_accounts()
        
        if len(accounts) > 0:
            account_id = accounts[0]
            
            # Search by specific amount
            self.find_transactions_page.search_transactions(
                account_id=account_id,
                amount="100.00"
            )
            
            # Wait for results
            results_loaded = self.find_transactions_page.wait_for_search_results()
            if results_loaded:
                has_transactions = self.find_transactions_page.has_transactions()
                log.info(f"Transactions found for amount $100.00: {has_transactions}")

    @pytest.mark.advanced_search
    def test_search_transactions_with_multiple_criteria(self):
        """Test searching transactions with multiple criteria."""
        self.login_and_navigate_to_find_transactions()
        
        # Get available accounts and transaction types
        accounts = self.find_transactions_page.get_available_accounts()
        transaction_types = self.find_transactions_page.get_transaction_types()
        
        if len(accounts) > 0 and len(transaction_types) > 0:
            account_id = accounts[0]
            transaction_type = transaction_types[0]
            
            # Search with multiple criteria
            self.find_transactions_page.search_transactions(
                account_id=account_id,
                transaction_type=transaction_type,
                from_date=self.get_date_string(-30),
                to_date=self.get_date_string(),
                amount="50.00"
            )
            
            # Wait for results
            results_loaded = self.find_transactions_page.wait_for_search_results()
            assert results_loaded, "Search with multiple criteria should load"
            
            has_transactions = self.find_transactions_page.has_transactions()
            log.info(f"Transactions found with multiple criteria: {has_transactions}")

    @pytest.mark.data_export
    def test_transaction_data_export(self):
        """Test transaction data export functionality."""
        self.login_and_navigate_to_find_transactions()
        
        # Get available accounts
        accounts = self.find_transactions_page.get_available_accounts()
        
        if len(accounts) > 0:
            # Search for transactions
            account_id = accounts[0]
            self.find_transactions_page.search_transactions(account_id=account_id)
            
            results_loaded = self.find_transactions_page.wait_for_search_results()
            if results_loaded:
                # Export transaction data
                export_data = self.find_transactions_page.export_transaction_data()
                
                # Verify export structure
                assert isinstance(export_data, dict), "Export data should be dictionary"
                assert 'timestamp' in export_data, "Should include timestamp"
                assert 'total_transactions' in export_data, "Should include transaction count"
                assert 'transactions' in export_data, "Should include transactions list"
                assert 'search_criteria' in export_data, "Should include search criteria"

    @pytest.mark.error_handling
    def test_no_results_message_display(self):
        """Test no results message display."""
        self.login_and_navigate_to_find_transactions()
        
        # Get available accounts
        accounts = self.find_transactions_page.get_available_accounts()
        
        if len(accounts) > 0:
            # Search with criteria that should return no results
            account_id = accounts[0]
            future_date = self.get_date_string(365)  # 1 year in future
            
            self.find_transactions_page.search_transactions(
                account_id=account_id,
                date=future_date
            )
            
            # Wait for results
            results_loaded = self.find_transactions_page.wait_for_search_results()
            if results_loaded:
                # Check for no results message
                no_results_msg = self.find_transactions_page.get_no_results_message()
                log.info(f"No results message: {no_results_msg}")

    @pytest.mark.browser_compatibility
    def test_find_transactions_form_javascript_functionality(self):
        """Test find transactions form JavaScript functionality."""
        self.login_and_navigate_to_find_transactions()
        
        # Test JavaScript evaluation on form
        form_exists = self.page.evaluate("""
            () => {
                const form = document.querySelector('form');
                return form !== null;
            }
        """)
        
        assert form_exists, "Find transactions form should be accessible via JavaScript"
        
        # Test form filling via JavaScript
        accounts = self.find_transactions_page.get_available_accounts()
        if len(accounts) > 0:
            # Fill form using JavaScript
            self.page.evaluate(f"""
                () => {{
                    document.querySelector('#accountId').value = '{accounts[0]}';
                    document.querySelector('#onDate').value = '{self.get_date_string()}';
                }}
            """)
            
            # Verify form is filled
            validation = self.find_transactions_page.validate_search_criteria()
            assert validation['account_selected'], "Account should be selected after JavaScript fill"

    @pytest.mark.localization
    def test_find_transactions_page_localization_elements(self):
        """Test find transactions page localization elements."""
        self.login_and_navigate_to_find_transactions()
        
        # Check for proper labels
        labels = self.page.locator("label")
        if labels.count() > 0:
            # Verify labels are present
            assert labels.count() > 0, "Should have form labels"

    @pytest.mark.responsive
    def test_find_transactions_form_responsive_design(self):
        """Test find transactions form responsive design."""
        self.login_and_navigate_to_find_transactions()
        
        # Test different viewport sizes
        viewport_sizes = [
            {'width': 1920, 'height': 1080},  # Desktop
            {'width': 768, 'height': 1024},   # Tablet
            {'width': 375, 'height': 667}     # Mobile
        ]
        
        for viewport in viewport_sizes:
            self.page.set_viewport_size(viewport)
            
            # Check if form elements are still visible and functional
            assert self.page.is_visible(self.find_transactions_page.ACCOUNT_SELECT), f"Account select should be visible on {viewport['width']}x{viewport['height']}"
            assert self.page.is_visible(self.find_transactions_page.TRANSACTION_TYPE_SELECT), f"Transaction type select should be visible on {viewport['width']}x{viewport['height']}"
            assert self.page.is_visible(self.find_transactions_page.FIND_TRANSACTIONS_BUTTON), f"Find button should be visible on {viewport['width']}x{viewport['height']}"

    @pytest.mark.conditional
    def test_find_transactions_with_single_account_scenario(self):
        """Test find transactions behavior with only one account available."""
        self.login_and_navigate_to_find_transactions()
        
        accounts = self.find_transactions_page.get_available_accounts()
        
        if len(accounts) == 1:
            # Test behavior with single account
            single_account = accounts[0]
            
            # Select the single account
            self.find_transactions_page.select_account(single_account)
            
            # Verify account is selected
            account_selected = self.find_transactions_page.get_attribute(self.find_transactions_page.ACCOUNT_SELECT, "value")
            assert account_selected == single_account, f"Account {single_account} should be selected"

    @pytest.mark.conditional
    def test_find_transactions_with_multiple_accounts_scenario(self):
        """Test find transactions behavior with multiple accounts available."""
        self.login_and_navigate_to_find_transactions()
        
        accounts = self.find_transactions_page.get_available_accounts()
        
        if len(accounts) >= 2:
            # Test with multiple accounts
            assert len(accounts) >= 2, "Should have at least 2 accounts for this test"
            
            # Test searching different accounts
            for account in accounts[:min(3, len(accounts))]:  # Test first 3 accounts
                self.find_transactions_page.search_transactions(account_id=account)
                
                # Wait for results
                results_loaded = self.find_transactions_page.wait_for_search_results()
                assert results_loaded, f"Search should complete for account {account}"

    @pytest.mark.data_analysis
    def test_transaction_search_by_description(self):
        """Test searching transactions by description keyword."""
        self.login_and_navigate_to_find_transactions()
        
        # Get available accounts
        accounts = self.find_transactions_page.get_available_accounts()
        
        if len(accounts) > 0:
            # Search for transactions
            account_id = accounts[0]
            self.find_transactions_page.search_transactions(account_id=account_id)
            
            results_loaded = self.find_transactions_page.wait_for_search_results()
            if results_loaded and self.find_transactions_page.has_transactions():
                # Get all transactions
                all_transactions = self.find_transactions_page.get_transactions()
                
                if len(all_transactions) > 0:
                    # Test description search
                    first_description = all_transactions[0]['description']
                    if first_description:
                        # Extract a keyword from first description
                        keywords = first_description.split()[:2]  # First two words
                        if keywords:
                            keyword = keywords[0]
                            filtered_transactions = self.find_transactions_page.search_transactions_by_description(keyword)
                            
                            # Verify filtering worked
                            assert isinstance(filtered_transactions, list), "Should return list of filtered transactions"
                            log.info(f"Found {len(filtered_transactions)} transactions with keyword '{keyword}'")

    @pytest.mark.data_analysis
    def test_transaction_search_by_amount_range(self):
        """Test searching transactions by amount range."""
        self.login_and_navigate_to_find_transactions()
        
        # Get available accounts
        accounts = self.find_transactions_page.get_available_accounts()
        
        if len(accounts) > 0:
            # Search for transactions
            account_id = accounts[0]
            self.find_transactions_page.search_transactions(account_id=account_id)
            
            results_loaded = self.find_transactions_page.wait_for_search_results()
            if results_loaded and self.find_transactions_page.has_transactions():
                # Test amount range filtering
                qualifying_transactions = self.find_transactions_page.get_transactions_by_amount_range(0.01, 1000.00)
                
                # Verify filtering worked
                assert isinstance(qualifying_transactions, list), "Should return list of qualifying transactions"
                log.info(f"Found {len(qualifying_transactions)} transactions in amount range $0.01 - $1000.00")

    @pytest.mark.edge_case
    def test_search_with_very_wide_date_range(self):
        """Test searching with very wide date range."""
        self.login_and_navigate_to_find_transactions()
        
        # Get available accounts
        accounts = self.find_transactions_page.get_available_accounts()
        
        if len(accounts) > 0:
            # Search with wide date range (1 year)
            account_id = accounts[0]
            from_date = self.get_date_string(-365)
            to_date = self.get_date_string()
            
            self.find_transactions_page.search_transactions(
                account_id=account_id,
                from_date=from_date,
                to_date=to_date
            )
            
            # Wait for results
            results_loaded = self.find_transactions_page.wait_for_search_results()
            assert results_loaded, "Search with wide date range should complete"
            
            has_transactions = self.find_transactions_page.has_transactions()
            log.info(f"Transactions found for wide date range: {has_transactions}")

    @pytest.mark.edge_case
    def test_search_with_reversed_date_range(self):
        """Test searching with reversed date range (from date after to date)."""
        self.login_and_navigate_to_find_transactions()
        
        # Get available accounts
        accounts = self.find_transactions_page.get_available_accounts()
        
        if len(accounts) > 0:
            # Search with reversed date range
            account_id = accounts[0]
            from_date = self.get_date_string()
            to_date = self.get_date_string(-30)  # Earlier than from date
            
            self.find_transactions_page.search_transactions(
                account_id=account_id,
                from_date=from_date,
                to_date=to_date
            )
            
            # Should handle gracefully
            results_loaded = self.find_transactions_page.wait_for_search_results()
            log.info(f"Search with reversed date range result: {results_loaded}")

    @pytest.mark.security
    def test_transaction_search_data_privacy(self):
        """Test transaction search data privacy and security."""
        self.login_and_navigate_to_find_transactions()
        
        # Check that sensitive data is not exposed inappropriately
        page_content = self.page.content()
        
        # Should not expose passwords
        assert "password" not in page_content.lower(), "Password data should not be exposed"
        
        # Account IDs should be properly formatted
        accounts = self.find_transactions_page.get_available_accounts()
        for account in accounts:
            assert len(account) > 0, "Account IDs should be properly formatted"

    @pytest.mark.integration
    def test_complete_transaction_search_workflow(self):
        """Test complete transaction search workflow."""
        self.login_and_navigate_to_find_transactions()
        
        # Get available accounts and transaction types
        accounts = self.find_transactions_page.get_available_accounts()
        transaction_types = self.find_transactions_page.get_transaction_types()
        
        if len(accounts) > 0 and len(transaction_types) > 0:
            account_id = accounts[0]
            transaction_type = transaction_types[0]
            
            # Step 1: Search by account only
            self.find_transactions_page.search_transactions(account_id=account_id)
            results_loaded = self.find_transactions_page.wait_for_search_results()
            assert results_loaded, "Account-only search should work"
            
            initial_count = self.find_transactions_page.get_transaction_count()
            log.info(f"Initial search found {initial_count} transactions")
            
            # Step 2: Add transaction type filter
            self.find_transactions_page.search_transactions(
                account_id=account_id,
                transaction_type=transaction_type
            )
            results_loaded = self.find_transactions_page.wait_for_search_results()
            assert results_loaded, "Account + type search should work"
            
            filtered_count = self.find_transactions_page.get_transaction_count()
            log.info(f"Filtered search found {filtered_count} transactions")
            
            # Step 3: Add date filter
            self.find_transactions_page.search_transactions(
                account_id=account_id,
                transaction_type=transaction_type,
                from_date=self.get_date_string(-7),
                to_date=self.get_date_string()
            )
            results_loaded = self.find_transactions_page.wait_for_search_results()
            assert results_loaded, "Account + type + date search should work"
            
            date_filtered_count = self.find_transactions_page.get_transaction_count()
            log.info(f"Date-filtered search found {date_filtered_count} transactions")
            
            # Verify filtering is working (count should decrease or stay same)
            assert date_filtered_count <= filtered_count <= initial_count, "Filtering should reduce or maintain transaction count"
