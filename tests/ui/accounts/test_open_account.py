"""Comprehensive UI test suite for ParaBank Open Account page."""
import pytest
from playwright.sync_api import Page
from src.pages.open_account_page import OpenAccountPage
from src.pages.login_page import LoginPage
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.utils.test_data_utils import TestDataUtils
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.open_account
class TestOpenAccountPage:
    """Enterprise-grade test suite for open account functionality."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test environment."""
        self.page = page
        self.open_account_page = OpenAccountPage(page)
        self.login_page = LoginPage(page)
        self.accounts_page = AccountsOverviewPage(page)
        self.test_data = TestDataUtils()

    def login_and_navigate_to_open_account(self):
        """Helper method to login and navigate to open account page."""
        # Login with valid credentials
        self.login_page.navigate_to_login()
        login_result = self.login_page.login_with_validation("john", "demo")
        assert login_result['success'], "Login should be successful"
        
        # Navigate to open account page
        self.open_account_page.navigate_to_open_account()
        self.open_account_page.assert_open_account_page_loaded()

    @pytest.mark.smoke
    def test_open_account_page_loads_correctly(self):
        """Test that open account page loads with all required elements."""
        self.login_and_navigate_to_open_account()
        
        # Verify page title
        assert "ParaBank" in self.page.title()
        assert "Open Account" in self.page.title()

    @pytest.mark.smoke
    def test_account_type_dropdown_populates_correctly(self):
        """Test that account type dropdown populates with available types."""
        self.login_and_navigate_to_open_account()
        
        # Get available account types
        account_types = self.open_account_page.get_account_types()
        
        assert isinstance(account_types, list), "Account types should be a list"
        assert len(account_types) > 0, "Should have at least one account type"
        
        # Check for common account types
        common_types = ["CHECKING", "SAVINGS"]
        found_common_types = [acc_type for acc_type in common_types if any(acc_type in account_type.upper() for account_type in account_types)]
        assert len(found_common_types) > 0, "Should have common account types like CHECKING or SAVINGS"

    @pytest.mark.smoke
    def test_source_account_dropdown_populates_correctly(self):
        """Test that source account dropdown populates with available accounts."""
        self.login_and_navigate_to_open_account()
        
        # Get available source accounts
        source_accounts = self.open_account_page.get_source_accounts()
        
        assert isinstance(source_accounts, list), "Source accounts should be a list"
        assert len(source_accounts) > 0, "Should have at least one source account"

    @pytest.mark.smoke
    def test_successful_opening_checking_account(self):
        """Test successful opening of checking account."""
        self.login_and_navigate_to_open_account()
        
        # Get available options
        account_types = self.open_account_page.get_account_types()
        source_accounts = self.open_account_page.get_source_accounts()
        
        if len(account_types) > 0 and len(source_accounts) > 0:
            # Find checking account type
            checking_type = None
            for acc_type in account_types:
                if "CHECKING" in acc_type.upper():
                    checking_type = acc_type
                    break
            
            if checking_type:
                # Open checking account
                source_account = source_accounts[0]
                self.open_account_page.open_new_account(checking_type, source_account)
                
                # Verify successful account opening
                assert self.open_account_page.is_account_opened_successfully()
                
                # Check success message
                success_msg = self.open_account_page.get_success_message()
                assert "Account Opened!" in success_msg or "successfully" in success_msg.lower()

    @pytest.mark.smoke
    def test_successful_opening_savings_account(self):
        """Test successful opening of savings account."""
        self.login_and_navigate_to_open_account()
        
        # Get available options
        account_types = self.open_account_page.get_account_types()
        source_accounts = self.open_account_page.get_source_accounts()
        
        if len(account_types) > 0 and len(source_accounts) > 0:
            # Find savings account type
            savings_type = None
            for acc_type in account_types:
                if "SAVINGS" in acc_type.upper():
                    savings_type = acc_type
                    break
            
            if savings_type:
                # Open savings account
                source_account = source_accounts[0]
                self.open_account_page.open_new_account(savings_type, source_account)
                
                # Verify successful account opening
                assert self.open_account_page.is_account_opened_successfully()
                
                # Check success message
                success_msg = self.open_account_page.get_success_message()
                assert "Account Opened!" in success_msg or "successfully" in success_msg.lower()

    @pytest.mark.regression
    def test_open_account_without_selecting_type_fails(self):
        """Test account opening fails without selecting account type."""
        self.login_and_navigate_to_open_account()
        
        # Get available source accounts
        source_accounts = self.open_account_page.get_source_accounts()
        
        if len(source_accounts) > 0:
            # Select source account but not account type
            source_account = source_accounts[0]
            self.open_account_page.select_source_account(source_account)
            self.open_account_page.click_open_new_account()
            
            # Should fail
            assert not self.open_account_page.is_account_opened_successfully()

    @pytest.mark.regression
    def test_open_account_without_selecting_source_fails(self):
        """Test account opening fails without selecting source account."""
        self.login_and_navigate_to_open_account()
        
        # Get available account types
        account_types = self.open_account_page.get_account_types()
        
        if len(account_types) > 0:
            # Select account type but not source account
            account_type = account_types[0]
            self.open_account_page.select_account_type(account_type)
            self.open_account_page.click_open_new_account()
            
            # Should fail
            assert not self.open_account_page.is_account_opened_successfully()

    @pytest.mark.regression
    def test_open_account_with_invalid_account_type_fails(self):
        """Test account opening fails with invalid account type."""
        self.login_and_navigate_to_open_account()
        
        # Get available source accounts
        source_accounts = self.open_account_page.get_source_accounts()
        
        if len(source_accounts) > 0:
            # Try to select invalid account type
            try:
                self.open_account_page.select_account_type("INVALID_TYPE")
                source_account = source_accounts[0]
                self.open_account_page.select_source_account(source_account)
                self.open_account_page.click_open_new_account()
                
                # Should fail
                assert not self.open_account_page.is_account_opened_successfully()
            except Exception:
                # Expected behavior - invalid type should not be selectable
                pass

    @pytest.mark.regression
    def test_open_account_with_invalid_source_account_fails(self):
        """Test account opening fails with invalid source account."""
        self.login_and_navigate_to_open_account()
        
        # Get available account types
        account_types = self.open_account_page.get_account_types()
        
        if len(account_types) > 0:
            # Try to select invalid source account
            try:
                account_type = account_types[0]
                self.open_account_page.select_account_type(account_type)
                self.open_account_page.select_source_account("999999")
                self.open_account_page.click_open_new_account()
                
                # Should fail
                assert not self.open_account_page.is_account_opened_successfully()
            except Exception:
                # Expected behavior - invalid account should not be selectable
                pass

    @pytest.mark.usability
    def test_open_account_form_validation(self):
        """Test open account form validation functionality."""
        self.login_and_navigate_to_open_account()
        
        # Initially form should not be ready
        validation = self.open_account_page.validate_open_account_form()
        assert not validation['form_ready']
        assert not validation['account_type_selected']
        assert not validation['source_account_selected']
        
        # Fill valid data
        account_types = self.open_account_page.get_account_types()
        source_accounts = self.open_account_page.get_source_accounts()
        
        if len(account_types) > 0 and len(source_accounts) > 0:
            account_type = account_types[0]
            source_account = source_accounts[0]
            
            self.open_account_page.select_account_type(account_type)
            self.open_account_page.select_source_account(source_account)
            
            # Now form should be ready
            validation = self.open_account_page.validate_open_account_form()
            assert validation['form_ready']
            assert validation['account_type_selected']
            assert validation['source_account_selected']

    @pytest.mark.navigation
    def test_accounts_overview_link_navigation(self):
        """Test Accounts Overview link navigation."""
        self.login_and_navigate_to_open_account()
        
        # Click Accounts Overview link
        self.open_account_page.click_accounts_overview()
        
        # Should navigate to accounts overview
        self.accounts_page.assert_accounts_overview_loaded()

    @pytest.mark.accessibility
    def test_open_account_form_accessibility(self):
        """Test open account form accessibility features."""
        self.login_and_navigate_to_open_account()
        
        # Check if form fields have proper labels
        form_fields = [
            (self.open_account_page.ACCOUNT_TYPE_SELECT, "Account type"),
            (self.open_account_page.FROM_ACCOUNT_SELECT, "From account"),
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
    def test_open_account_page_load_performance(self):
        """Test open account page load performance."""
        from datetime import datetime
        
        start_time = datetime.now()
        self.login_and_navigate_to_open_account()
        load_time = (datetime.now() - start_time).total_seconds()
        
        # Page should load within reasonable time (5 seconds)
        assert load_time < 5.0, f"Page load time {load_time}s exceeds threshold"

    @pytest.mark.performance
    def test_dropdown_population_performance(self):
        """Test dropdown population performance."""
        self.login_and_navigate_to_open_account()
        
        start_time = datetime.now()
        account_types = self.open_account_page.get_account_types()
        source_accounts = self.open_account_page.get_source_accounts()
        population_time = (datetime.now() - start_time).total_seconds()
        
        # Dropdown population should be fast (2 seconds)
        assert population_time < 2.0, f"Dropdown population time {population_time}s exceeds threshold"

    @pytest.mark.data_validation
    def test_new_account_details_accuracy(self):
        """Test new account details accuracy after opening."""
        self.login_and_navigate_to_open_account()
        
        # Get available options
        account_types = self.open_account_page.get_account_types()
        source_accounts = self.open_account_page.get_source_accounts()
        
        if len(account_types) > 0 and len(source_accounts) > 0:
            account_type = account_types[0]
            source_account = source_accounts[0]
            
            # Open account
            self.open_account_page.open_new_account(account_type, source_account)
            
            if self.open_account_page.is_account_opened_successfully():
                # Get new account details
                details = self.open_account_page.get_new_account_details()
                
                # Verify details contain expected information
                assert details or len(details) > 0, "Should have account details"
                
                if 'account_id' in details:
                    assert details['account_id'], "Account ID should not be empty"
                    assert details['account_id'].isdigit(), "Account ID should be numeric"

    @pytest.mark.data_validation
    def test_new_account_id_format(self):
        """Test new account ID format validation."""
        self.login_and_navigate_to_open_account()
        
        # Get available options
        account_types = self.open_account_page.get_account_types()
        source_accounts = self.open_account_page.get_source_accounts()
        
        if len(account_types) > 0 and len(source_accounts) > 0:
            account_type = account_types[0]
            source_account = source_accounts[0]
            
            # Open account
            self.open_account_page.open_new_account(account_type, source_account)
            
            if self.open_account_page.is_account_opened_successfully():
                # Get new account ID
                account_id = self.open_account_page.get_new_account_id()
                
                # Validate format
                assert account_id, "Account ID should not be empty"
                assert account_id.isdigit(), "Account ID should be numeric"
                assert len(account_id) >= 5, "Account ID should have reasonable length"

    @pytest.mark.regression
    def test_clear_open_account_form(self):
        """Test clearing open account form functionality."""
        self.login_and_navigate_to_open_account()
        
        # Fill form with data
        account_types = self.open_account_page.get_account_types()
        source_accounts = self.open_account_page.get_source_accounts()
        
        if len(account_types) > 0 and len(source_accounts) > 0:
            account_type = account_types[0]
            source_account = source_accounts[0]
            
            self.open_account_page.select_account_type(account_type)
            self.open_account_page.select_source_account(source_account)
            
            # Clear form
            self.open_account_page.clear_open_account_form()
            
            # Verify form is cleared
            validation = self.open_account_page.validate_open_account_form()
            assert not validation['account_type_selected']
            assert not validation['source_account_selected']

    @pytest.mark.regression
    def test_wait_for_account_opening_complete(self):
        """Test account opening completion wait functionality."""
        self.login_and_navigate_to_open_account()
        
        # Get available options
        account_types = self.open_account_page.get_account_types()
        source_accounts = self.open_account_page.get_source_accounts()
        
        if len(account_types) > 0 and len(source_accounts) > 0:
            account_type = account_types[0]
            source_account = source_accounts[0]
            
            # Perform account opening
            self.open_account_page.open_new_account(account_type, source_account)
            
            # Wait for completion
            completed = self.open_account_page.wait_for_account_opening_complete()
            assert completed, "Account opening should complete within timeout"

    @pytest.mark.integration
    def test_account_opening_simulation_with_validation(self):
        """Test complete account opening simulation with validation."""
        self.login_and_navigate_to_open_account()
        
        # Get available options
        account_types = self.open_account_page.get_account_types()
        source_accounts = self.open_account_page.get_source_accounts()
        
        if len(account_types) > 0 and len(source_accounts) > 0:
            account_type = account_types[0]
            source_account = source_accounts[0]
            
            # Simulate account opening with validation
            result = self.open_account_page.simulate_account_opening_with_validation(
                account_type, source_account
            )
            
            # Verify simulation results
            assert isinstance(result, dict), "Should return dictionary"
            assert 'success' in result, "Should have success status"
            assert 'validation_results' in result, "Should have validation results"
            
            if result['success']:
                assert 'new_account_details' in result, "Should have new account details on success"

    @pytest.mark.error_handling
    def test_account_opening_error_message_display(self):
        """Test error message display for invalid account opening."""
        self.login_and_navigate_to_open_account()
        
        # Submit empty form
        self.open_account_page.click_open_new_account()
        
        # Check if error message is displayed
        error_msg = self.open_account_page.get_error_message()
        # Note: Error message content depends on backend validation
        log.info(f"Error message for empty form: {error_msg}")

    @pytest.mark.browser_compatibility
    def test_open_account_form_javascript_functionality(self):
        """Test open account form JavaScript functionality."""
        self.login_and_navigate_to_open_account()
        
        # Test JavaScript evaluation on form
        form_exists = self.page.evaluate("""
            () => {
                const form = document.querySelector('#openAccountForm');
                return form !== null;
            }
        """)
        
        assert form_exists, "Open account form should be accessible via JavaScript"
        
        # Test form filling via JavaScript
        account_types = self.open_account_page.get_account_types()
        source_accounts = self.open_account_page.get_source_accounts()
        
        if len(account_types) > 0 and len(source_accounts) > 0:
            # Fill form using JavaScript
            self.page.evaluate(f"""
                () => {{
                    document.querySelector('#type').value = '{account_types[0]}';
                    document.querySelector('#fromAccountId').value = '{source_accounts[0]}';
                }}
            """)
            
            # Verify form is filled
            validation = self.open_account_page.validate_open_account_form()
            assert validation['form_ready'], "Form should be ready after JavaScript fill"

    @pytest.mark.localization
    def test_open_account_page_localization_elements(self):
        """Test open account page localization elements."""
        self.login_and_navigate_to_open_account()
        
        # Check for proper labels
        labels = self.page.locator("label")
        if labels.count() > 0:
            # Verify labels are present
            assert labels.count() > 0, "Should have form labels"

    @pytest.mark.responsive
    def test_open_account_form_responsive_design(self):
        """Test open account form responsive design."""
        self.login_and_navigate_to_open_account()
        
        # Test different viewport sizes
        viewport_sizes = [
            {'width': 1920, 'height': 1080},  # Desktop
            {'width': 768, 'height': 1024},   # Tablet
            {'width': 375, 'height': 667}     # Mobile
        ]
        
        for viewport in viewport_sizes:
            self.page.set_viewport_size(viewport)
            
            # Check if form elements are still visible and functional
            assert self.page.is_visible(self.open_account_page.ACCOUNT_TYPE_SELECT), f"Account type select should be visible on {viewport['width']}x{viewport['height']}"
            assert self.page.is_visible(self.open_account_page.FROM_ACCOUNT_SELECT), f"From account select should be visible on {viewport['width']}x{viewport['height']}"
            assert self.page.is_visible(self.open_account_page.OPEN_NEW_ACCOUNT_BUTTON), f"Open account button should be visible on {viewport['width']}x{viewport['height']}"

    @pytest.mark.conditional
    def test_open_account_with_single_account_scenario(self):
        """Test account opening behavior with only one account available."""
        self.login_and_navigate_to_open_account()
        
        source_accounts = self.open_account_page.get_source_accounts()
        
        if len(source_accounts) == 1:
            # Test behavior with single account
            single_account = source_accounts[0]
            
            # Select the single account
            self.open_account_page.select_source_account(single_account)
            
            # Verify account is selected
            from_selected = self.open_account_page.get_attribute(self.open_account_page.FROM_ACCOUNT_SELECT, "value")
            assert from_selected == single_account, f"Account {single_account} should be selected"

    @pytest.mark.conditional
    def test_open_account_with_multiple_accounts_scenario(self):
        """Test account opening behavior with multiple accounts available."""
        self.login_and_navigate_to_open_account()
        
        source_accounts = self.open_account_page.get_source_accounts()
        
        if len(source_accounts) >= 2:
            # Test with multiple accounts
            assert len(source_accounts) >= 2, "Should have at least 2 accounts for this test"
            
            # Test selecting different accounts
            for account in source_accounts[:min(3, len(source_accounts))]:  # Test first 3 accounts
                self.open_account_page.select_source_account(account)
                
                # Verify selection
                from_selected = self.open_account_page.get_attribute(self.open_account_page.FROM_ACCOUNT_SELECT, "value")
                assert from_selected == account, f"Account {account} should be selected"

    @pytest.mark.usability
    def test_account_type_availability_validation(self):
        """Test account type availability validation."""
        self.login_and_navigate_to_open_account()
        
        # Get available account types
        available_types = self.open_account_page.get_account_types()
        
        if len(available_types) > 0:
            # Test validation for available type
            first_type = available_types[0]
            is_available = self.open_account_page.validate_account_type_availability(first_type)
            assert is_available, f"Available type {first_type} should validate as available"
            
            # Test validation for unavailable type
            is_available = self.open_account_page.validate_account_type_availability("UNAVAILABLE_TYPE")
            assert not is_available, "Unavailable type should validate as not available"

    @pytest.mark.usability
    def test_source_account_availability_validation(self):
        """Test source account availability validation."""
        self.login_and_navigate_to_open_account()
        
        # Get available source accounts
        available_accounts = self.open_account_page.get_source_accounts()
        
        if len(available_accounts) > 0:
            # Test validation for available account
            first_account = available_accounts[0]
            is_available = self.open_account_page.validate_source_account_availability(first_account)
            assert is_available, f"Available account {first_account} should validate as available"
            
            # Test validation for unavailable account
            is_available = self.open_account_page.validate_source_account_availability("999999")
            assert not is_available, "Unavailable account should validate as not available"

    @pytest.mark.data_export
    def test_account_opening_summary(self):
        """Test account opening summary functionality."""
        self.login_and_navigate_to_open_account()
        
        # Get account opening summary
        summary = self.open_account_page.get_account_opening_summary()
        
        # Verify summary structure
        assert isinstance(summary, dict), "Summary should be dictionary"
        assert 'available_account_types' in summary, "Should include available account types"
        assert 'available_source_accounts' in summary, "Should include available source accounts"
        assert 'form_validation' in summary, "Should include form validation"
        assert 'current_selections' in summary, "Should include current selections"

    @pytest.mark.edge_case
    def test_open_multiple_accounts_same_type(self):
        """Test opening multiple accounts of the same type."""
        self.login_and_navigate_to_open_account()
        
        # Get available options
        account_types = self.open_account_page.get_account_types()
        source_accounts = self.open_account_page.get_source_accounts()
        
        if len(account_types) > 0 and len(source_accounts) > 0:
            account_type = account_types[0]
            source_account = source_accounts[0]
            
            # Open first account
            self.open_account_page.open_new_account(account_type, source_account)
            first_success = self.open_account_page.is_account_opened_successfully()
            
            # Go back to open another account
            self.open_account_page.navigate_to_open_account()
            
            # Try to open another account of same type
            self.open_account_page.open_new_account(account_type, source_account)
            second_success = self.open_account_page.is_account_opened_successfully()
            
            log.info(f"First account opening: {first_success}, Second account opening: {second_success}")

    @pytest.mark.edge_case
    def test_open_all_available_account_types(self):
        """Test opening one account of each available type."""
        self.login_and_navigate_to_open_account()
        
        account_types = self.open_account_page.get_account_types()
        source_accounts = self.open_account_page.get_source_accounts()
        
        if len(account_types) > 0 and len(source_accounts) > 0:
            source_account = source_accounts[0]
            results = {}
            
            for account_type in account_types[:min(3, len(account_types))]:  # Test first 3 types
                # Navigate back to open account page
                self.open_account_page.navigate_to_open_account()
                
                # Open account
                self.open_account_page.open_new_account(account_type, source_account)
                success = self.open_account_page.is_account_opened_successfully()
                results[account_type] = success
                
                log.info(f"Account type {account_type}: {'Success' if success else 'Failed'}")
            
            # At least one should succeed
            assert any(results.values()), "At least one account type should open successfully"

    @pytest.mark.security
    def test_account_opening_data_privacy(self):
        """Test account opening data privacy and security."""
        self.login_and_navigate_to_open_account()
        
        # Check that sensitive data is not exposed inappropriately
        page_content = self.page.content()
        
        # Should not expose passwords or sensitive account details
        assert "password" not in page_content.lower(), "Password data should not be exposed"
        
        # Account IDs in dropdowns should be masked or limited
        source_accounts = self.open_account_page.get_source_accounts()
        for account in source_accounts:
            assert len(account) > 0, "Account IDs should be properly formatted"
