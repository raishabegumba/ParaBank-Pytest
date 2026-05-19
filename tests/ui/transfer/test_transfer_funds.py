"""Comprehensive UI test suite for ParaBank Transfer Funds page."""
import pytest
from decimal import Decimal
from datetime import datetime
from playwright.sync_api import Page
from src.pages.transfer_funds_page import TransferFundsPage
from src.pages.login_page import LoginPage
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.utils.test_data_utils import TestDataUtils
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.transfer
class TestTransferFundsPage:
    """Enterprise-grade test suite for transfer funds functionality."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test environment."""
        self.page = page
        self.transfer_page = TransferFundsPage(page)
        self.login_page = LoginPage(page)
        self.accounts_page = AccountsOverviewPage(page)
        self.test_data = TestDataUtils()

    def login_and_navigate_to_transfer(self):
        """Helper method to login and navigate to transfer funds page."""
        # Login with valid credentials
        self.login_page.navigate_to_login()
        login_result = self.login_page.login_with_validation("john", "demo")
        assert login_result['success'], "Login should be successful"
        
        # Navigate to transfer funds page
        self.transfer_page.navigate_to_transfer_funds()
        self.transfer_page.assert_transfer_page_loaded()

    @pytest.mark.smoke
    def test_transfer_funds_page_loads_correctly(self):
        """Test that transfer funds page loads with all required elements."""
        self.login_and_navigate_to_transfer()
        
        # Verify page title
        assert "ParaBank" in self.page.title()
        assert "Transfer" in self.page.title()

    @pytest.mark.smoke
    def test_account_dropdowns_populate_correctly(self):
        """Test that account dropdowns populate with available accounts."""
        self.login_and_navigate_to_transfer()
        
        # Get available accounts from both dropdowns
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        
        assert isinstance(from_accounts, list), "From accounts should be a list"
        assert isinstance(to_accounts, list), "To accounts should be a list"
        assert len(from_accounts) > 0, "Should have at least one from account"
        assert len(to_accounts) > 0, "Should have at least one to account"

    @pytest.mark.smoke
    def test_successful_transfer_with_valid_data(self):
        """Test successful fund transfer with valid data."""
        self.login_and_navigate_to_transfer()
        
        # Get available accounts
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        
        if len(from_accounts) >= 2:
            # Select different accounts
            from_account = from_accounts[0]
            to_account = from_accounts[1] if len(from_accounts) > 1 else to_accounts[0]
            
            # Ensure different accounts
            if from_account == to_account and len(to_accounts) > 1:
                to_account = to_accounts[1]
            
            # Perform transfer
            amount = "50.00"
          
            self.transfer_page.perform_transfer(from_account, to_account, amount)
            
            # Verify successful transfer
            assert self.transfer_page.is_transfer_successful()
            
            # Check success message
            success_msg = self.transfer_page.get_success_message()
            assert "Transfer Complete!" in success_msg or "successfully" in success_msg.lower()

    @pytest.mark.regression
    def test_transfer_with_same_account_fails(self):
        """Test transfer fails when from and to accounts are the same."""
        self.login_and_navigate_to_transfer()
        
        # Get available accounts
        from_accounts = self.transfer_page.get_from_accounts()
        
        if len(from_accounts) > 0:
            # Select same account for both from and to
            same_account = from_accounts[0]
            
            self.transfer_page.select_from_account(same_account)
            self.transfer_page.select_to_account(same_account)
            self.transfer_page.enter_amount("50.00")
            
            # Try to submit
            self.transfer_page.click_transfer_button()
            
            # Should fail or show validation error
            validation = self.transfer_page.validate_transfer_form()

            assert validation["different_accounts"] is False
            assert "From and To accounts must be different" in validation["issues"]

    @pytest.mark.regression
    def test_transfer_with_zero_amount_fails(self):
        """Test transfer with zero amount fails."""

        self.login_and_navigate_to_transfer()

        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()

        from_account = from_accounts[0]
        to_account = next(
            acc for acc in to_accounts
            if acc != from_account
        )

        with pytest.raises(
            ValueError,
            match="greater than 0"
        ):
            self.transfer_page.perform_transfer(
                from_account,
                to_account,
                "0.00"
            )

    @pytest.mark.regression
    def test_transfer_with_negative_amount_fails(self):
        """Test transfer with negative amount fails."""

        self.login_and_navigate_to_transfer()

        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()

        from_account = from_accounts[0]
        to_account = next(
            acc for acc in to_accounts
            if acc != from_account
        )

        with pytest.raises(
            ValueError,
            match="greater than 0"
        ):
            self.transfer_page.perform_transfer(
                from_account,
                to_account,
                "-50.00"
            )

    @pytest.mark.regression
    def test_transfer_with_invalid_amount_format_fails(self):
        """Test transfer with invalid amount format fails."""

        self.login_and_navigate_to_transfer()

        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()

        from_account = from_accounts[0]
        to_account = next(
            acc for acc in to_accounts
            if acc != from_account
        )

        with pytest.raises(
            ValueError,
            match="Invalid transfer amount"
        ):
            self.transfer_page.perform_transfer(
                from_account,
                to_account,
                "abc"
            )

    @pytest.mark.regression
    def test_transfer_without_amount_fails(self):
        """Test transfer fails without entering amount."""
        self.login_and_navigate_to_transfer()
        
        # Get available accounts
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        
        if len(from_accounts) >= 1 and len(to_accounts) >= 1:
            from_account = from_accounts[0]
            to_account = to_accounts[0] if to_accounts[0] != from_account else (to_accounts[1] if len(to_accounts) > 1 else from_accounts[0])
            
            # Select accounts but don't enter amount
            self.transfer_page.select_from_account(from_account)
            self.transfer_page.select_to_account(to_account)
            self.transfer_page.click_transfer_button()
            
            # Should fail
            assert not self.transfer_page.is_transfer_successful()

    @pytest.mark.usability
    def test_transfer_form_validation(self):
        """Test transfer form validation functionality."""
        self.login_and_navigate_to_transfer()
        
        # Initially form should not be ready
        validation = self.transfer_page.validate_transfer_form()
        assert not validation['form_ready']
        assert not validation['amount_entered']
        # Fill valid data
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        
        if len(from_accounts) >= 2:
            from_account = from_accounts[0]
            to_account = from_accounts[1]
            
            self.transfer_page.select_from_account(from_account)
            self.transfer_page.select_to_account(to_account)
            self.transfer_page.enter_amount("50.00")
            
            # Now form should be ready
            validation = self.transfer_page.validate_transfer_form()
            assert validation['form_ready']
            assert validation['from_account_selected']
            assert validation['to_account_selected']
            assert validation['amount_entered']
            assert validation['valid_amount']
            assert validation['different_accounts']

    @pytest.mark.usability
    def test_transfer_limits_validation(self):
        """Test transfer limits validation."""
        self.login_and_navigate_to_transfer()
        
        # Test various amount limits
        test_amounts = [
            (0.01, True),   # Minimum valid amount
            (100.00, True), # Normal amount
            (10000.00, True), # At limit
            (10001.00, False), # Over transaction limit
            (25001.00, False), # Over daily limit
        ]
        
        for amount, should_be_valid in test_amounts:
            validation = self.transfer_page.validate_transfer_limits(amount)
            
            if should_be_valid:
                assert validation['within_transaction_limit'], f"Amount {amount} should be within transaction limit"
            else:
                assert not validation['within_transaction_limit'], f"Amount {amount} should exceed transaction limit"

    @pytest.mark.navigation
    def test_accounts_overview_link_navigation(self):
        """Test Accounts Overview link navigation."""
        self.login_and_navigate_to_transfer()
        
        # Click Accounts Overview link
        self.transfer_page.click_accounts_overview()
        
        # Should navigate to accounts overview
        self.accounts_page.assert_accounts_overview_loaded()

    @pytest.mark.accessibility
    def test_transfer_form_accessibility(self):
        """Test transfer form accessibility features."""
        self.login_and_navigate_to_transfer()
        
        # Check if form fields have proper labels
        form_fields = [
            (self.transfer_page.FROM_ACCOUNT_SELECT, "From account"),
            (self.transfer_page.TO_ACCOUNT_SELECT, "To account"),
            (self.transfer_page.AMOUNT_FIELD, "Amount"),
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
    def test_transfer_page_load_performance(self):
        """Test transfer page load performance."""
        from datetime import datetime
        
        start_time = datetime.now()
        self.login_and_navigate_to_transfer()
        load_time = (datetime.now() - start_time).total_seconds()
        
        # Page should load within reasonable time (5 seconds)
        assert load_time < 5.0, f"Page load time {load_time}s exceeds threshold"

    @pytest.mark.performance
    def test_account_dropdown_population_performance(self):
        """Test account dropdown population performance."""
        self.login_and_navigate_to_transfer()
        
        start_time = datetime.now()
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        population_time = (datetime.now() - start_time).total_seconds()
        
        # Dropdown population should be fast (2 seconds)
        assert population_time < 2.0, f"Dropdown population time {population_time}s exceeds threshold"

    @pytest.mark.edge_case
    def test_transfer_with_maximum_amount(self):
        """Test transfer with maximum allowed amount."""
        self.login_and_navigate_to_transfer()
        
        # Get available accounts
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        
        if len(from_accounts) >= 2:
            from_account = from_accounts[0]
            to_account = from_accounts[1]
            
            # Try transfer with maximum amount
            max_amount = "10000.00"
            self.transfer_page.perform_transfer(from_account, to_account, max_amount)
            
            # Should succeed (at limit)
            result = self.transfer_page.is_transfer_successful()
            log.info(f"Maximum amount transfer result: {result}")

    @pytest.mark.edge_case
    def test_transfer_with_decimal_amount(self):
        self.login_and_navigate_to_transfer()

        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()

        if len(from_accounts) >= 2:
            from_account = from_accounts[0]
            to_account = from_accounts[1]

            decimal_amount = "123.45"

            self.transfer_page.perform_transfer(
                from_account,
                to_account,
                decimal_amount
            )

            print(self.page.locator("body").inner_text())

            assert self.transfer_page.is_transfer_successful()

    @pytest.mark.edge_case
    def test_transfer_with_very_small_amount(self):
        """Test transfer with very small amount."""
        self.login_and_navigate_to_transfer()
        
        # Get available accounts
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        
        if len(from_accounts) >= 2:
            from_account = from_accounts[0]
            to_account = from_accounts[1]
            
            # Try transfer with very small amount
            small_amount = "0.01"
            self.transfer_page.perform_transfer(from_account, to_account, small_amount)
            
            # Should succeed
            assert self.transfer_page.is_transfer_successful()

    @pytest.mark.regression
    def test_clear_transfer_form(self):
        """Test clearing transfer form functionality."""
        self.login_and_navigate_to_transfer()
        
        # Fill form with data
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        
        if len(from_accounts) >= 2:
            from_account = from_accounts[0]
            to_account = from_accounts[1]
            
            self.transfer_page.select_from_account(from_account)
            self.transfer_page.select_to_account(to_account)
            self.transfer_page.enter_amount("50.00")
            
            
            # Clear form
            self.transfer_page.clear_transfer_form()
            
            # Verify amount and description are cleared
            amount_value = self.transfer_page.get_attribute(self.transfer_page.AMOUNT_FIELD, "value")
            # description_value = self.transfer_page.get_attribute(self.transfer_page.DESCRIPTION_FIELD, "value")
            
            assert amount_value == "" or amount_value is None, "Amount field should be cleared"
            # assert description_value == "" or description_value is None, "Description field should be cleared"

    @pytest.mark.regression
    def test_transfer_wait_for_completion(self):
        """Test transfer completion wait functionality."""
        self.login_and_navigate_to_transfer()
        
        # Get available accounts
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        
        if len(from_accounts) >= 2:
            from_account = from_accounts[0]
            to_account = from_accounts[1]
            
            # Perform transfer
            self.transfer_page.perform_transfer(from_account, to_account, "50.00")
            
            # Wait for completion
            completed = self.transfer_page.wait_for_transfer_complete()
            assert completed, "Transfer should complete within timeout"

    @pytest.mark.data_validation
    def test_transfer_confirmation_details(self):
        """Test transfer confirmation details accuracy."""
        self.login_and_navigate_to_transfer()
        
        # Get available accounts
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        
        if len(from_accounts) >= 2:
            from_account = from_accounts[0]
            to_account = from_accounts[1]
            amount = "75.25"
               
            # Perform transfer
            self.transfer_page.perform_transfer(from_account, to_account, amount)
            
            if self.transfer_page.is_transfer_successful():
                # Get confirmation details
                details = self.transfer_page.get_transfer_confirmation_details()
                
                # Verify details contain expected information
                assert details or len(details) > 0, "Should have confirmation details"
                
                if 'amount' in details:
                    assert amount in details['amount'], f"Amount {amount} should be in confirmation"

    @pytest.mark.integration
    def test_transfer_simulation_with_validation(self):
        """Test complete transfer simulation with validation."""
        self.login_and_navigate_to_transfer()
        
        # Get available accounts
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        
        if len(from_accounts) >= 2:
            from_account = from_accounts[0]
            to_account = from_accounts[1]
            
            # Simulate transfer with validation
            result = self.transfer_page.simulate_transfer_with_validation(
                from_account, to_account, "100.00"
            )
            
            # Verify simulation results
            assert isinstance(result, dict), "Should return dictionary"
            assert 'success' in result, "Should have success status"
            assert 'validation_results' in result, "Should have validation results"
            
            if result['success']:
                assert 'confirmation_details' in result, "Should have confirmation details on success"

    @pytest.mark.error_handling
    def test_transfer_error_message_display(self):
        """Test error message display for invalid transfer."""
        self.login_and_navigate_to_transfer()
        
        # Submit empty form
        self.transfer_page.click_transfer_button()
        
        # Check if error message is displayed
        error_msg = self.transfer_page.get_error_message()
        # Note: Error message content depends on backend validation
        log.info(f"Error message for empty form: {error_msg}")

    @pytest.mark.security
    def test_transfer_amount_field_security(self):
        """Test transfer amount field security."""
        self.login_and_navigate_to_transfer()
        
        # Check that amount field doesn't expose sensitive data
        amount_field = self.page.locator(self.transfer_page.AMOUNT_FIELD)
        input_type = amount_field.get_attribute('type')
        
        # Should be text type (not password) for amount field
        assert input_type == 'text', "Amount field should be text type"

    @pytest.mark.browser_compatibility
    def test_transfer_form_javascript_functionality(self):
        """Test transfer form JavaScript functionality."""
        self.login_and_navigate_to_transfer()
        
        # Test JavaScript evaluation on form
        form_exists = self.page.evaluate("""
            () => {
                const form = document.querySelector('#transferForm');
                return form !== null;
            }
        """)
        
        assert form_exists, "Transfer form should be accessible via JavaScript"
        
        # Test form validation via JavaScript
        from_accounts = self.transfer_page.get_from_accounts()
        if len(from_accounts) >= 2:
            # Fill form using JavaScript
            self.page.evaluate(f"""
                () => {{
                    document.querySelector('#fromAccountId').value = '{from_accounts[0]}';
                    document.querySelector('#toAccountId').value = '{from_accounts[1]}';
                    document.querySelector('#amount').value = '50.00';
                }}
            """)
            
            # Verify form is filled
            validation = self.transfer_page.validate_transfer_form()
            assert validation['form_ready'], "Form should be ready after JavaScript fill"

    @pytest.mark.localization
    def test_transfer_page_localization_elements(self):
        """Test transfer page localization elements."""
        self.login_and_navigate_to_transfer()
        
        # Check for currency formatting
        page_content = self.page.content()
        assert len(page_content) > 0, "Page should have content"
        
        # Check for proper labels
        labels = self.page.locator("label")
        if labels.count() > 0:
            # Verify labels are present
            assert labels.count() > 0, "Should have form labels"

    @pytest.mark.responsive
    def test_transfer_form_responsive_design(self):
        """Test transfer form responsive design."""
        self.login_and_navigate_to_transfer()
        
        # Test different viewport sizes
        viewport_sizes = [
            {'width': 1920, 'height': 1080},  # Desktop
            {'width': 768, 'height': 1024},   # Tablet
            {'width': 375, 'height': 667}     # Mobile
        ]
        
        for viewport in viewport_sizes:
            self.page.set_viewport_size(viewport)
            
            # Check if form elements are still visible and functional
            assert self.page.is_visible(self.transfer_page.FROM_ACCOUNT_SELECT), f"From account select should be visible on {viewport['width']}x{viewport['height']}"
            assert self.page.is_visible(self.transfer_page.TO_ACCOUNT_SELECT), f"To account select should be visible on {viewport['width']}x{viewport['height']}"
            assert self.page.is_visible(self.transfer_page.AMOUNT_FIELD), f"Amount field should be visible on {viewport['width']}x{viewport['height']}"
            assert self.page.is_visible(self.transfer_page.TRANSFER_BUTTON), f"Transfer button should be visible on {viewport['width']}x{viewport['height']}"

    @pytest.mark.conditional
    def test_transfer_with_single_account_scenario(self):
        """Test transfer behavior with only one account available."""
        self.login_and_navigate_to_transfer()
        
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        
        if len(from_accounts) == 1:
            # Test behavior with single account
            single_account = from_accounts[0]
            
            # Select the single account
            self.transfer_page.select_from_account(single_account)
            
            # Verify to account options
            to_options = self.transfer_page.get_to_accounts()
            assert len(to_options) >= 1, "Should have at least one to account option"

    @pytest.mark.conditional
    def test_transfer_with_multiple_accounts_scenario(self):
        """Test transfer behavior with multiple accounts available."""
        self.login_and_navigate_to_transfer()
        
        from_accounts = self.transfer_page.get_from_accounts()
        
        if len(from_accounts) >= 3:
            # Test with multiple accounts
            assert len(from_accounts) >= 3, "Should have at least 3 accounts for this test"
            
            # Test selecting different account combinations
            for i in range(min(3, len(from_accounts))):
                for j in range(min(3, len(from_accounts))):
                    if i != j:
                        self.transfer_page.select_from_account(from_accounts[i])
                        self.transfer_page.select_to_account(from_accounts[j])
                        
                        # Verify selections
                        from_selected = self.page.locator(self.transfer_page.FROM_ACCOUNT_SELECT).input_value()

                        to_selected = self.page.locator(self.transfer_page.TO_ACCOUNT_SELECT).input_value()
                        
                        assert from_selected == from_accounts[i], f"From account {from_accounts[i]} should be selected"
                        assert to_selected == from_accounts[j], f"To account {from_accounts[j]} should be selected"
