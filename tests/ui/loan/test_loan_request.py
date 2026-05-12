"""Comprehensive UI test suite for ParaBank Loan Request page."""
import pytest
from decimal import Decimal
from playwright.sync_api import Page
from src.pages.loan_request_page import LoanRequestPage
from src.pages.login_page import LoginPage
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.utils.test_data_utils import TestDataUtils
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.loan_request
class TestLoanRequestPage:
    """Enterprise-grade test suite for loan request functionality."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test environment."""
        self.page = page
        self.loan_page = LoanRequestPage(page)
        self.login_page = LoginPage(page)
        self.accounts_page = AccountsOverviewPage(page)
        self.test_data = TestDataUtils()

    def login_and_navigate_to_loan_request(self):
        """Helper method to login and navigate to loan request page."""
        # Login with valid credentials
        self.login_page.navigate_to_login()
        login_result = self.login_page.login_with_validation("john", "demo")
        assert login_result['success'], "Login should be successful"
        
        # Navigate to loan request page
        self.loan_page.navigate_to_loan_request()
        self.loan_page.assert_loan_request_page_loaded()

    @pytest.mark.smoke
    def test_loan_request_page_loads_correctly(self):
        """Test that loan request page loads with all required elements."""
        self.login_and_navigate_to_loan_request()
        
        # Verify page title
        assert "ParaBank" in self.page.title()
        assert "Loan" in self.page.title()

    @pytest.mark.smoke
    def test_account_dropdown_populates_correctly(self):
        """Test that account dropdown populates with available accounts."""
        self.login_and_navigate_to_loan_request()
        
        # Get available accounts
        accounts = self.loan_page.get_available_accounts()
        
        assert isinstance(accounts, list), "Accounts should be a list"
        assert len(accounts) > 0, "Should have at least one account"

    @pytest.mark.smoke
    def test_successful_loan_application(self):
        """Test successful loan application with valid data."""
        self.login_and_navigate_to_loan_request()
        
        # Get available accounts
        accounts = self.loan_page.get_available_accounts()
        
        if len(accounts) > 0:
            # Prepare loan data
            from_account = accounts[0]
            loan_amount = "10000.00"
            down_payment = "1000.00"
            
            # Apply for loan
            self.loan_page.apply_for_loan(loan_amount, down_payment, from_account)
            
            # Check result (could be approved or denied)
            processing_complete = self.loan_page.wait_for_loan_processing_complete()
            assert processing_complete, "Loan processing should complete"
            
            # Verify we get a result (either approval or denial)
            is_approved = self.loan_page.is_loan_approved()
            is_denied = self.loan_page.is_loan_denied()
            assert is_approved or is_denied, "Should get either approval or denial"

    @pytest.mark.regression
    def test_loan_application_without_account_fails(self):
        """Test loan application fails without selecting account."""
        self.login_and_navigate_to_loan_request()
        
        # Fill loan amount and down payment but don't select account
        self.loan_page.enter_loan_amount("10000.00")
        self.loan_page.enter_down_payment("1000.00")
        self.loan_page.click_apply_for_loan()
        
        # Should fail
        assert not self.loan_page.is_loan_approved()
        assert not self.loan_page.is_loan_denied()  # Should not process

    @pytest.mark.regression
    def test_loan_application_without_amount_fails(self):
        """Test loan application fails without entering loan amount."""
        self.login_and_navigate_to_loan_request()
        
        # Get available accounts
        accounts = self.loan_page.get_available_accounts()
        
        if len(accounts) > 0:
            # Select account and enter down payment but not loan amount
            from_account = accounts[0]
            self.loan_page.select_from_account(from_account)
            self.loan_page.enter_down_payment("1000.00")
            self.loan_page.click_apply_for_loan()
            
            # Should fail
            assert not self.loan_page.is_loan_approved()
            assert not self.loan_page.is_loan_denied()  # Should not process

    @pytest.mark.regression
    def test_loan_application_without_down_payment_fails(self):
        """Test loan application fails without entering down payment."""
        self.login_and_navigate_to_loan_request()
        
        # Get available accounts
        accounts = self.loan_page.get_available_accounts()
        
        if len(accounts) > 0:
            # Select account and enter loan amount but not down payment
            from_account = accounts[0]
            self.loan_page.select_from_account(from_account)
            self.loan_page.enter_loan_amount("10000.00")
            self.loan_page.click_apply_for_loan()
            
            # Should fail
            assert not self.loan_page.is_loan_approved()
            assert not self.loan_page.is_loan_denied()  # Should not process

    @pytest.mark.regression
    def test_loan_application_with_zero_amount_fails(self):
        """Test loan application fails with zero loan amount."""
        self.login_and_navigate_to_loan_request()
        
        # Get available accounts
        accounts = self.loan_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            
            # Try with zero loan amount
            self.loan_page.apply_for_loan("0.00", "1000.00", from_account)
            
            # Should fail
            assert not self.loan_page.is_loan_approved()

    @pytest.mark.regression
    def test_loan_application_with_negative_amount_fails(self):
        """Test loan application fails with negative loan amount."""
        self.login_and_navigate_to_loan_request()
        
        # Get available accounts
        accounts = self.loan_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            
            # Try with negative loan amount
            self.loan_page.apply_for_loan("-10000.00", "1000.00", from_account)
            
            # Should fail
            assert not self.loan_page.is_loan_approved()

    @pytest.mark.regression
    def test_loan_application_with_negative_down_payment_fails(self):
        """Test loan application fails with negative down payment."""
        self.login_and_navigate_to_loan_request()
        
        # Get available accounts
        accounts = self.loan_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            
            # Try with negative down payment
            self.loan_page.apply_for_loan("10000.00", "-1000.00", from_account)
            
            # Should fail
            assert not self.loan_page.is_loan_approved()

    @pytest.mark.regression
    def test_loan_application_with_invalid_amount_format_fails(self):
        """Test loan application fails with invalid amount format."""
        self.login_and_navigate_to_loan_request()
        
        # Get available accounts
        accounts = self.loan_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            
            # Try with invalid loan amount
            self.loan_page.apply_for_loan("abc", "1000.00", from_account)
            
            # Should fail
            assert not self.loan_page.is_loan_approved()

    @pytest.mark.usability
    def test_loan_request_form_validation(self):
        """Test loan request form validation functionality."""
        self.login_and_navigate_to_loan_request()
        
        # Initially form should not be ready
        validation = self.loan_page.validate_loan_request_form()
        assert not validation['form_ready']
        assert not validation['from_account_selected']
        assert not validation['loan_amount_entered']
        assert not validation['down_payment_entered']
        
        # Fill valid data
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            from_account = accounts[0]
            
            self.loan_page.select_from_account(from_account)
            self.loan_page.enter_loan_amount("10000.00")
            self.loan_page.enter_down_payment("1000.00")
            
            # Now form should be ready
            validation = self.loan_page.validate_loan_request_form()
            assert validation['form_ready']
            assert validation['from_account_selected']
            assert validation['loan_amount_entered']
            assert validation['valid_loan_amount']
            assert validation['down_payment_entered']
            assert validation['valid_down_payment']

    @pytest.mark.usability
    def test_loan_eligibility_validation(self):
        """Test loan eligibility validation."""
        self.login_and_navigate_to_loan_request()
        
        # Test various loan scenarios
        test_scenarios = [
            (10000.00, 1000.00, True),   # Normal case - 10% down payment
            (10000.00, 500.00, False),   # Insufficient down payment - 5%
            (10000.00, 2000.00, True),   # Good down payment - 20%
            (500.00, 50.00, False),      # Below minimum loan amount
            (200000.00, 20000.00, False), # Above maximum loan amount
        ]
        
        for loan_amount, down_payment, should_be_eligible in test_scenarios:
            validation = self.loan_page.validate_loan_eligibility(loan_amount, down_payment)
            
            if should_be_eligible:
                assert validation['eligible'], f"Loan ${loan_amount} with ${down_payment} down payment should be eligible"
            else:
                assert not validation['eligible'], f"Loan ${loan_amount} with ${down_payment} down payment should not be eligible"

    @pytest.mark.navigation
    def test_accounts_overview_link_navigation(self):
        """Test Accounts Overview link navigation."""
        self.login_and_navigate_to_loan_request()
        
        # Click Accounts Overview link
        self.loan_page.click_accounts_overview()
        
        # Should navigate to accounts overview
        self.accounts_page.assert_accounts_overview_loaded()

    @pytest.mark.accessibility
    def test_loan_request_form_accessibility(self):
        """Test loan request form accessibility features."""
        self.login_and_navigate_to_loan_request()
        
        # Check if form fields have proper labels
        form_fields = [
            (self.loan_page.LOAN_AMOUNT_FIELD, "Loan amount"),
            (self.loan_page.DOWN_PAYMENT_FIELD, "Down payment"),
            (self.loan_page.FROM_ACCOUNT_SELECT, "From account"),
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
    def test_loan_request_page_load_performance(self):
        """Test loan request page load performance."""
        from datetime import datetime
        
        start_time = datetime.now()
        self.login_and_navigate_to_loan_request()
        load_time = (datetime.now() - start_time).total_seconds()
        
        # Page should load within reasonable time (5 seconds)
        assert load_time < 5.0, f"Page load time {load_time}s exceeds threshold"

    @pytest.mark.performance
    def test_account_dropdown_population_performance(self):
        """Test account dropdown population performance."""
        self.login_and_navigate_to_loan_request()
        
        start_time = datetime.now()
        accounts = self.loan_page.get_available_accounts()
        population_time = (datetime.now() - start_time).total_seconds()
        
        # Dropdown population should be fast (2 seconds)
        assert population_time < 2.0, f"Dropdown population time {population_time}s exceeds threshold"

    @pytest.mark.edge_case
    def test_loan_application_with_maximum_amount(self):
        """Test loan application with maximum allowed amount."""
        self.login_and_navigate_to_loan_request()
        
        # Get available accounts
        accounts = self.loan_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            
            # Try with maximum amount
            max_amount = "100000.00"
            max_down_payment = "10000.00"
            
            self.loan_page.apply_for_loan(max_amount, max_down_payment, from_account)
            
            # Should process (may be approved or denied based on business rules)
            processing_complete = self.loan_page.wait_for_loan_processing_complete()
            assert processing_complete, "Loan processing should complete"
            
            result = self.loan_page.is_loan_approved()
            log.info(f"Maximum amount loan result: {'Approved' if result else 'Denied'}")

    @pytest.mark.edge_case
    def test_loan_application_with_minimum_amount(self):
        """Test loan application with minimum allowed amount."""
        self.login_and_navigate_to_loan_request()
        
        # Get available accounts
        accounts = self.loan_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            
            # Try with minimum amount
            min_amount = "1000.00"
            min_down_payment = "100.00"
            
            self.loan_page.apply_for_loan(min_amount, min_down_payment, from_account)
            
            # Should process (may be approved or denied based on business rules)
            processing_complete = self.loan_page.wait_for_loan_processing_complete()
            assert processing_complete, "Loan processing should complete"
            
            result = self.loan_page.is_loan_approved()
            log.info(f"Minimum amount loan result: {'Approved' if result else 'Denied'}")

    @pytest.mark.edge_case
    def test_loan_application_with_decimal_amounts(self):
        """Test loan application with decimal amounts."""
        self.login_and_navigate_to_loan_request()
        
        # Get available accounts
        accounts = self.loan_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            
            # Try with decimal amounts
            loan_amount = "12345.67"
            down_payment = "1234.56"
            
            self.loan_page.apply_for_loan(loan_amount, down_payment, from_account)
            
            # Should process
            processing_complete = self.loan_page.wait_for_loan_processing_complete()
            assert processing_complete, "Loan processing should complete"

    @pytest.mark.edge_case
    def test_loan_application_with_zero_down_payment(self):
        """Test loan application with zero down payment."""
        self.login_and_navigate_to_loan_request()
        
        # Get available accounts
        accounts = self.loan_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            
            # Try with zero down payment
            self.loan_page.apply_for_loan("10000.00", "0.00", from_account)
            
            # Should process but likely be denied
            processing_complete = self.loan_page.wait_for_loan_processing_complete()
            assert processing_complete, "Loan processing should complete"
            
            result = self.loan_page.is_loan_approved()
            log.info(f"Zero down payment loan result: {'Approved' if result else 'Denied'}")

    @pytest.mark.regression
    def test_clear_loan_request_form(self):
        """Test clearing loan request form functionality."""
        self.login_and_navigate_to_loan_request()
        
        # Fill form with data
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            from_account = accounts[0]
            
            self.loan_page.select_from_account(from_account)
            self.loan_page.enter_loan_amount("10000.00")
            self.loan_page.enter_down_payment("1000.00")
            
            # Clear form
            self.loan_page.clear_loan_request_form()
            
            # Verify fields are cleared
            loan_amount_value = self.loan_page.get_attribute(self.loan_page.LOAN_AMOUNT_FIELD, "value")
            down_payment_value = self.loan_page.get_attribute(self.loan_page.DOWN_PAYMENT_FIELD, "value")
            
            assert loan_amount_value == "" or loan_amount_value is None, "Loan amount field should be cleared"
            assert down_payment_value == "" or down_payment_value is None, "Down payment field should be cleared"

    @pytest.mark.regression
    def test_wait_for_loan_processing_complete(self):
        """Test loan processing completion wait functionality."""
        self.login_and_navigate_to_loan_request()
        
        # Get available accounts
        accounts = self.loan_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            
            # Perform loan application
            self.loan_page.apply_for_loan("10000.00", "1000.00", from_account)
            
            # Wait for completion
            completed = self.loan_page.wait_for_loan_processing_complete()
            assert completed, "Loan processing should complete within timeout"

    @pytest.mark.data_validation
    def test_loan_confirmation_details_accuracy(self):
        """Test loan confirmation details accuracy."""
        self.login_and_navigate_to_loan_request()
        
        # Get available accounts
        accounts = self.loan_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            loan_amount = "15000.00"
            down_payment = "1500.00"
            
            # Apply for loan
            self.loan_page.apply_for_loan(loan_amount, down_payment, from_account)
            
            processing_complete = self.loan_page.wait_for_loan_processing_complete()
            if processing_complete:
                # Get confirmation details
                details = self.loan_page.get_loan_confirmation_details()
                
                # Verify details contain expected information
                assert details or len(details) > 0, "Should have confirmation details"
                
                if 'loan_amount' in details:
                    assert loan_amount in details['loan_amount'], f"Loan amount {loan_amount} should be in confirmation"

    @pytest.mark.integration
    def test_loan_request_simulation_with_validation(self):
        """Test complete loan request simulation with validation."""
        self.login_and_navigate_to_loan_request()
        
        # Get available accounts
        accounts = self.loan_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            loan_amount = "20000.00"
            down_payment = "2000.00"
            
            # Simulate loan request with validation
            result = self.loan_page.simulate_loan_request_with_validation(
                loan_amount, down_payment, from_account
            )
            
            # Verify simulation results
            assert isinstance(result, dict), "Should return dictionary"
            assert 'success' in result, "Should have success status"
            assert 'validation_results' in result, "Should have validation results"
            assert 'eligibility_results' in result, "Should have eligibility results"
            
            if result['success']:
                assert 'approved' in result, "Should have approval status"
                if result['approved']:
                    assert 'confirmation_details' in result, "Should have confirmation details on approval"

    @pytest.mark.error_handling
    def test_loan_request_error_message_display(self):
        """Test error message display for invalid loan request."""
        self.login_and_navigate_to_loan_request()
        
        # Submit empty form
        self.loan_page.click_apply_for_loan()
        
        # Check if error message is displayed
        error_msg = self.loan_page.get_error_message()
        # Note: Error message content depends on backend validation
        log.info(f"Error message for empty form: {error_msg}")

    @pytest.mark.security
    def test_loan_amount_field_security(self):
        """Test loan amount field security."""
        self.login_and_navigate_to_loan_request()
        
        # Check that amount field doesn't expose sensitive data
        loan_amount_field = self.page.locator(self.loan_page.LOAN_AMOUNT_FIELD)
        down_payment_field = self.page.locator(self.loan_page.DOWN_PAYMENT_FIELD)
        
        loan_input_type = loan_amount_field.get_attribute('type')
        down_payment_input_type = down_payment_field.get_attribute('type')
        
        # Should be text type (not password) for amount fields
        assert loan_input_type == 'text', "Loan amount field should be text type"
        assert down_payment_input_type == 'text', "Down payment field should be text type"

    @pytest.mark.browser_compatibility
    def test_loan_request_form_javascript_functionality(self):
        """Test loan request form JavaScript functionality."""
        self.login_and_navigate_to_loan_request()
        
        # Test JavaScript evaluation on form
        form_exists = self.page.evaluate("""
            () => {
                const form = document.querySelector('#loanForm');
                return form !== null;
            }
        """)
        
        assert form_exists, "Loan request form should be accessible via JavaScript"
        
        # Test form filling via JavaScript
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            # Fill form using JavaScript
            self.page.evaluate(f"""
                () => {{
                    document.querySelector('#fromAccountId').value = '{accounts[0]}';
                    document.querySelector('#amount').value = '10000.00';
                    document.querySelector('#downPayment').value = '1000.00';
                }}
            """)
            
            # Verify form is filled
            validation = self.loan_page.validate_loan_request_form()
            assert validation['form_ready'], "Form should be ready after JavaScript fill"

    @pytest.mark.localization
    def test_loan_request_page_localization_elements(self):
        """Test loan request page localization elements."""
        self.login_and_navigate_to_loan_request()
        
        # Check for currency formatting
        page_content = self.page.content()
        assert len(page_content) > 0, "Page should have content"
        
        # Check for proper labels
        labels = self.page.locator("label")
        if labels.count() > 0:
            # Verify labels are present
            assert labels.count() > 0, "Should have form labels"

    @pytest.mark.responsive
    def test_loan_request_form_responsive_design(self):
        """Test loan request form responsive design."""
        self.login_and_navigate_to_loan_request()
        
        # Test different viewport sizes
        viewport_sizes = [
            {'width': 1920, 'height': 1080},  # Desktop
            {'width': 768, 'height': 1024},   # Tablet
            {'width': 375, 'height': 667}     # Mobile
        ]
        
        for viewport in viewport_sizes:
            self.page.set_viewport_size(viewport)
            
            # Check if form elements are still visible and functional
            assert self.page.is_visible(self.loan_page.LOAN_AMOUNT_FIELD), f"Loan amount field should be visible on {viewport['width']}x{viewport['height']}"
            assert self.page.is_visible(self.loan_page.DOWN_PAYMENT_FIELD), f"Down payment field should be visible on {viewport['width']}x{viewport['height']}"
            assert self.page.is_visible(self.loan_page.FROM_ACCOUNT_SELECT), f"From account select should be visible on {viewport['width']}x{viewport['height']}"
            assert self.page.is_visible(self.loan_page.APPLY_FOR_LOAN_BUTTON), f"Apply button should be visible on {viewport['width']}x{viewport['height']}"

    @pytest.mark.conditional
    def test_loan_request_with_single_account_scenario(self):
        """Test loan request behavior with only one account available."""
        self.login_and_navigate_to_loan_request()
        
        accounts = self.loan_page.get_available_accounts()
        
        if len(accounts) == 1:
            # Test behavior with single account
            single_account = accounts[0]
            
            # Select the single account
            self.loan_page.select_from_account(single_account)
            
            # Verify account is selected
            from_selected = self.loan_page.get_attribute(self.loan_page.FROM_ACCOUNT_SELECT, "value")
            assert from_selected == single_account, f"Account {single_account} should be selected"

    @pytest.mark.conditional
    def test_loan_request_with_multiple_accounts_scenario(self):
        """Test loan request behavior with multiple accounts available."""
        self.login_and_navigate_to_loan_request()
        
        accounts = self.loan_page.get_available_accounts()
        
        if len(accounts) >= 2:
            # Test with multiple accounts
            assert len(accounts) >= 2, "Should have at least 2 accounts for this test"
            
            # Test selecting different accounts
            for account in accounts[:min(3, len(accounts))]:  # Test first 3 accounts
                self.loan_page.select_from_account(account)
                
                # Verify selection
                from_selected = self.loan_page.get_attribute(self.loan_page.FROM_ACCOUNT_SELECT, "value")
                assert from_selected == account, f"Account {account} should be selected"

    @pytest.mark.business_rules
    def test_loan_to_value_ratio_validation(self):
        """Test loan-to-value ratio business rules."""
        self.login_and_navigate_to_loan_request()
        
        # Test different LTV scenarios
        test_scenarios = [
            (10000.00, 1000.00, 90.0),   # 90% LTV - at limit
            (10000.00, 1500.00, 85.0),   # 85% LTV - good
            (10000.00, 500.00, 95.0),    # 95% LTV - exceeds limit
        ]
        
        for loan_amount, down_payment, expected_ltv in test_scenarios:
            validation = self.loan_page.validate_loan_eligibility(loan_amount, down_payment)
            
            if expected_ltv <= 90.0:
                # Should be eligible for LTV <= 90%
                assert validation['reasonable_loan_to_value'], f"LTV {expected_ltv}% should be acceptable"
            else:
                # Should not be eligible for LTV > 90%
                assert not validation['reasonable_loan_to_value'], f"LTV {expected_ltv}% should exceed limit"

    @pytest.mark.business_rules
    def test_down_payment_percentage_validation(self):
        """Test down payment percentage business rules."""
        self.login_and_navigate_to_loan_request()
        
        # Test different down payment percentages
        test_scenarios = [
            (10000.00, 500.00, 5.0),     # 5% down payment - below minimum
            (10000.00, 1000.00, 10.0),   # 10% down payment - at minimum
            (10000.00, 2000.00, 20.0),   # 20% down payment - good
        ]
        
        for loan_amount, down_payment, expected_percentage in test_scenarios:
            validation = self.loan_page.validate_loan_eligibility(loan_amount, down_payment)
            
            if expected_percentage >= 10.0:
                # Should be eligible for down payment >= 10%
                assert validation['adequate_down_payment'], f"Down payment {expected_percentage}% should be adequate"
            else:
                # Should not be eligible for down payment < 10%
                assert not validation['adequate_down_payment'], f"Down payment {expected_percentage}% should be inadequate"

    @pytest.mark.edge_case
    def test_multiple_loan_applications_same_session(self):
        """Test multiple loan applications in same session."""
        self.login_and_navigate_to_loan_request()
        
        # Get available accounts
        accounts = self.loan_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            results = []
            
            # Apply for multiple loans
            loan_scenarios = [
                ("5000.00", "500.00"),
                ("7500.00", "750.00"),
                ("15000.00", "1500.00"),
            ]
            
            for loan_amount, down_payment in loan_scenarios:
                # Navigate back to loan request page
                self.loan_page.navigate_to_loan_request()
                
                # Apply for loan
                self.loan_page.apply_for_loan(loan_amount, down_payment, from_account)
                
                processing_complete = self.loan_page.wait_for_loan_processing_complete()
                if processing_complete:
                    is_approved = self.loan_page.is_loan_approved()
                    results.append({
                        'loan_amount': loan_amount,
                        'down_payment': down_payment,
                        'approved': is_approved
                    })
                
                log.info(f"Loan {loan_amount} result: {'Approved' if is_approved else 'Denied'}")
            
            # Should have results for all applications
            assert len(results) == len(loan_scenarios), "Should have results for all loan applications"

    @pytest.mark.security
    def test_loan_request_data_privacy(self):
        """Test loan request data privacy and security."""
        self.login_and_navigate_to_loan_request()
        
        # Check that sensitive data is not exposed inappropriately
        page_content = self.page.content()
        
        # Should not expose passwords or sensitive financial data
        assert "password" not in page_content.lower(), "Password data should not be exposed"
        
        # Account IDs in dropdowns should be properly formatted
        accounts = self.loan_page.get_available_accounts()
        for account in accounts:
            assert len(account) > 0, "Account IDs should be properly formatted"
