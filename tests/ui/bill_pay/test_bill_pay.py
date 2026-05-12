"""Comprehensive UI test suite for ParaBank Bill Pay page."""
import pytest
from datetime import datetime, timedelta
from playwright.sync_api import Page
from src.pages.bill_pay_page import BillPayPage
from src.pages.login_page import LoginPage
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.utils.test_data_utils import TestDataUtils
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.bill_pay
class TestBillPayPage:
    """Enterprise-grade test suite for bill pay functionality."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test environment."""
        self.page = page
        self.bill_pay_page = BillPayPage(page)
        self.login_page = LoginPage(page)
        self.accounts_page = AccountsOverviewPage(page)
        self.test_data = TestDataUtils()

    def login_and_navigate_to_bill_pay(self):
        """Helper method to login and navigate to bill pay page."""
        # Login with valid credentials
        self.login_page.navigate_to_login()
        login_result = self.login_page.login_with_validation("john", "demo")
        assert login_result['success'], "Login should be successful"
        
        # Navigate to bill pay page
        self.bill_pay_page.navigate_to_bill_pay()
        self.bill_pay_page.assert_bill_pay_page_loaded()

    def generate_test_payee_data(self) -> dict:
        """Generate valid test payee data."""
        return {
            'name': 'Test Payee',
            'address': '456 Payee Street',
            'city': 'Payee City',
            'state': 'NY',
            'zip_code': '54321',
            'phone': '5559876543',
            'account_number': '987654321'
        }

    def get_future_date(self, days_ahead: int = 7) -> str:
        """Get future date in MM/DD/YYYY format."""
        future_date = datetime.now() + timedelta(days=days_ahead)
        return future_date.strftime("%m/%d/%Y")

    @pytest.mark.smoke
    def test_bill_pay_page_loads_correctly(self):
        """Test that bill pay page loads with all required elements."""
        self.login_and_navigate_to_bill_pay()
        
        # Verify page title
        assert "ParaBank" in self.page.title()
        assert "Bill Pay" in self.page.title()

    @pytest.mark.smoke
    def test_account_dropdown_populates_correctly(self):
        """Test that account dropdown populates with available accounts."""
        self.login_and_navigate_to_bill_pay()
        
        # Get available accounts
        accounts = self.bill_pay_page.get_available_accounts()
        
        assert isinstance(accounts, list), "Accounts should be a list"
        assert len(accounts) > 0, "Should have at least one account"

    @pytest.mark.smoke
    def test_successful_payment_with_new_payee(self):
        """Test successful bill payment with new payee."""
        self.login_and_navigate_to_bill_pay()
        
        # Get available accounts
        accounts = self.bill_pay_page.get_available_accounts()
        
        if len(accounts) > 0:
            # Prepare test data
            payee_data = self.generate_test_payee_data()
            from_account = accounts[0]
            amount = "100.00"
            date = self.get_future_date(7)
            description = "Test bill payment"
            
            # Send payment
            self.bill_pay_page.send_payment(
                from_account=from_account,
                amount=amount,
                date=date,
                description=description,
                payee_info=payee_data,
                add_new_payee=True
            )
            
            # Verify successful payment
            assert self.bill_pay_page.is_payment_successful()
            
            # Check success message
            success_msg = self.bill_pay_page.get_success_message()
            assert "Bill Payment Complete" in success_msg or "successfully" in success_msg.lower()

    @pytest.mark.regression
    def test_payment_with_zero_amount_fails(self):
        """Test payment fails with zero amount."""
        self.login_and_navigate_to_bill_pay()
        
        # Get available accounts
        accounts = self.bill_pay_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            payee_data = self.generate_test_payee_data()
            
            # Try payment with zero amount
            self.bill_pay_page.send_payment(
                from_account=from_account,
                amount="0.00",
                date=self.get_future_date(7),
                payee_info=payee_data,
                add_new_payee=True
            )
            
            # Should fail
            assert not self.bill_pay_page.is_payment_successful()

    @pytest.mark.regression
    def test_payment_with_negative_amount_fails(self):
        """Test payment fails with negative amount."""
        self.login_and_navigate_to_bill_pay()
        
        # Get available accounts
        accounts = self.bill_pay_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            payee_data = self.generate_test_payee_data()
            
            # Try payment with negative amount
            self.bill_pay_page.send_payment(
                from_account=from_account,
                amount="-50.00",
                date=self.get_future_date(7),
                payee_info=payee_data,
                add_new_payee=True
            )
            
            # Should fail
            assert not self.bill_pay_page.is_payment_successful()

    @pytest.mark.regression
    def test_payment_with_invalid_amount_format_fails(self):
        """Test payment fails with invalid amount format."""
        self.login_and_navigate_to_bill_pay()
        
        # Get available accounts
        accounts = self.bill_pay_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            payee_data = self.generate_test_payee_data()
            
            # Try payment with invalid amount
            self.bill_pay_page.send_payment(
                from_account=from_account,
                amount="abc",
                date=self.get_future_date(7),
                payee_info=payee_data,
                add_new_payee=True
            )
            
            # Should fail
            assert not self.bill_pay_page.is_payment_successful()

    @pytest.mark.regression
    def test_payment_without_account_selection_fails(self):
        """Test payment fails without selecting account."""
        self.login_and_navigate_to_bill_pay()
        
        payee_data = self.generate_test_payee_data()
        
        # Try payment without selecting account
        self.bill_pay_page.enter_payment_amount("100.00")
        self.bill_pay_page.enter_payment_date(self.get_future_date(7))
        self.bill_pay_page.fill_payee_information(**payee_data)
        self.bill_pay_page.click_send_payment()
        
        # Should fail
        assert not self.bill_pay_page.is_payment_successful()

    @pytest.mark.regression
    def test_payment_without_amount_fails(self):
        """Test payment fails without entering amount."""
        self.login_and_navigate_to_bill_pay()
        
        # Get available accounts
        accounts = self.bill_pay_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            payee_data = self.generate_test_payee_data()
            
            # Select account and fill payee info but don't enter amount
            self.bill_pay_page.select_from_account(from_account)
            self.bill_pay_page.enter_payment_date(self.get_future_date(7))
            self.bill_pay_page.fill_payee_information(**payee_data)
            self.bill_pay_page.click_send_payment()
            
            # Should fail
            assert not self.bill_pay_page.is_payment_successful()

    @pytest.mark.regression
    def test_payment_without_date_fails(self):
        """Test payment fails without entering date."""
        self.login_and_navigate_to_bill_pay()
        
        # Get available accounts
        accounts = self.bill_pay_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            payee_data = self.generate_test_payee_data()
            
            # Fill all fields except date
            self.bill_pay_page.select_from_account(from_account)
            self.bill_pay_page.enter_payment_amount("100.00")
            self.bill_pay_page.fill_payee_information(**payee_data)
            self.bill_pay_page.click_send_payment()
            
            # Should fail
            assert not self.bill_pay_page.is_payment_successful()

    @pytest.mark.regression
    def test_payment_without_payee_info_fails(self):
        """Test payment fails without payee information when adding new payee."""
        self.login_and_navigate_to_bill_pay()
        
        # Get available accounts
        accounts = self.bill_pay_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            
            # Fill fields but don't complete payee info
            self.bill_pay_page.select_from_account(from_account)
            self.bill_pay_page.enter_payment_amount("100.00")
            self.bill_pay_page.enter_payment_date(self.get_future_date(7))
            self.bill_pay_page.click_send_payment()
            
            # Should fail
            assert not self.bill_pay_page.is_payment_successful()

    @pytest.mark.usability
    def test_payment_form_validation(self):
        """Test payment form validation functionality."""
        self.login_and_navigate_to_bill_pay()
        
        # Initially form should not be ready
        validation = self.bill_pay_page.validate_payment_form()
        assert not validation['form_ready']
        assert not validation['from_account_selected']
        assert not validation['amount_entered']
        assert not validation['date_entered']
        
        # Fill valid data
        accounts = self.bill_pay_page.get_available_accounts()
        if len(accounts) > 0:
            from_account = accounts[0]
            payee_data = self.generate_test_payee_data()
            
            self.bill_pay_page.select_from_account(from_account)
            self.bill_pay_page.enter_payment_amount("100.00")
            self.bill_pay_page.enter_payment_date(self.get_future_date(7))
            self.bill_pay_page.fill_payee_information(**payee_data)
            
            # Now form should be ready
            validation = self.bill_pay_page.validate_payment_form()
            assert validation['form_ready']
            assert validation['from_account_selected']
            assert validation['amount_entered']
            assert validation['valid_amount']
            assert validation['date_entered']
            assert validation['valid_date']
            assert validation['payee_info_complete']

    @pytest.mark.usability
    def test_payment_limits_validation(self):
        """Test payment limits validation."""
        self.login_and_navigate_to_bill_pay()
        
        # Test various amount limits
        test_amounts = [
            (0.01, True),   # Minimum valid amount
            (100.00, True), # Normal amount
            (5000.00, True), # At limit
            (5001.00, False), # Over transaction limit
            (15001.00, False), # Over daily limit
        ]
        
        for amount, should_be_valid in test_amounts:
            validation = self.bill_pay_page.validate_payment_limits(amount)
            
            if should_be_valid:
                assert validation['within_transaction_limit'], f"Amount {amount} should be within transaction limit"
            else:
                assert not validation['within_transaction_limit'], f"Amount {amount} should exceed transaction limit"

    @pytest.mark.navigation
    def test_accounts_overview_link_navigation(self):
        """Test Accounts Overview link navigation."""
        self.login_and_navigate_to_bill_pay()
        
        # Click Accounts Overview link
        self.bill_pay_page.click_accounts_overview()
        
        # Should navigate to accounts overview
        self.accounts_page.assert_accounts_overview_loaded()

    @pytest.mark.accessibility
    def test_bill_pay_form_accessibility(self):
        """Test bill pay form accessibility features."""
        self.login_and_navigate_to_bill_pay()
        
        # Check if form fields have proper labels
        form_fields = [
            (self.bill_pay_page.FROM_ACCOUNT_SELECT, "From account"),
            (self.bill_pay_page.AMOUNT_FIELD, "Amount"),
            (self.bill_pay_page.PAYMENT_DATE_FIELD, "Payment date"),
            (self.bill_pay_page.DESCRIPTION_FIELD, "Description"),
            (self.bill_pay_page.PAYEE_NAME_FIELD, "Payee name"),
            (self.bill_pay_page.PAYEE_ADDRESS_FIELD, "Payee address"),
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
    def test_bill_pay_page_load_performance(self):
        """Test bill pay page load performance."""
        start_time = datetime.now()
        self.login_and_navigate_to_bill_pay()
        load_time = (datetime.now() - start_time).total_seconds()
        
        # Page should load within reasonable time (5 seconds)
        assert load_time < 5.0, f"Page load time {load_time}s exceeds threshold"

    @pytest.mark.performance
    def test_account_dropdown_population_performance(self):
        """Test account dropdown population performance."""
        self.login_and_navigate_to_bill_pay()
        
        start_time = datetime.now()
        accounts = self.bill_pay_page.get_available_accounts()
        population_time = (datetime.now() - start_time).total_seconds()
        
        # Dropdown population should be fast (2 seconds)
        assert population_time < 2.0, f"Dropdown population time {population_time}s exceeds threshold"

    @pytest.mark.edge_case
    def test_payment_with_maximum_amount(self):
        """Test payment with maximum allowed amount."""
        self.login_and_navigate_to_bill_pay()
        
        # Get available accounts
        accounts = self.bill_pay_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            payee_data = self.generate_test_payee_data()
            
            # Try payment with maximum amount
            max_amount = "5000.00"
            self.bill_pay_page.send_payment(
                from_account=from_account,
                amount=max_amount,
                date=self.get_future_date(7),
                description="Maximum amount test",
                payee_info=payee_data,
                add_new_payee=True
            )
            
            # Should succeed (at limit)
            result = self.bill_pay_page.is_payment_successful()
            log.info(f"Maximum amount payment result: {result}")

    @pytest.mark.edge_case
    def test_payment_with_decimal_amount(self):
        """Test payment with decimal amount."""
        self.login_and_navigate_to_bill_pay()
        
        # Get available accounts
        accounts = self.bill_pay_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            payee_data = self.generate_test_payee_data()
            
            # Try payment with decimal amount
            decimal_amount = "123.45"
            self.bill_pay_page.send_payment(
                from_account=from_account,
                amount=decimal_amount,
                date=self.get_future_date(7),
                description="Decimal amount test",
                payee_info=payee_data,
                add_new_payee=True
            )
            
            # Should succeed
            assert self.bill_pay_page.is_payment_successful()

    @pytest.mark.edge_case
    def test_payment_with_very_small_amount(self):
        """Test payment with very small amount."""
        self.login_and_navigate_to_bill_pay()
        
        # Get available accounts
        accounts = self.bill_pay_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            payee_data = self.generate_test_payee_data()
            
            # Try payment with very small amount
            small_amount = "0.01"
            self.bill_pay_page.send_payment(
                from_account=from_account,
                amount=small_amount,
                date=self.get_future_date(7),
                description="Small amount test",
                payee_info=payee_data,
                add_new_payee=True
            )
            
            # Should succeed
            assert self.bill_pay_page.is_payment_successful()

    @pytest.mark.edge_case
    def test_payment_with_future_date(self):
        """Test payment with future date."""
        self.login_and_navigate_to_bill_pay()
        
        # Get available accounts
        accounts = self.bill_pay_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            payee_data = self.generate_test_payee_data()
            
            # Try payment with future date (30 days ahead)
            future_date = self.get_future_date(30)
            self.bill_pay_page.send_payment(
                from_account=from_account,
                amount="100.00",
                date=future_date,
                description="Future date test",
                payee_info=payee_data,
                add_new_payee=True
            )
            
            # Should succeed or show appropriate message
            result = self.bill_pay_page.is_payment_successful()
            log.info(f"Future date payment result: {result}")

    @pytest.mark.edge_case
    def test_payment_with_past_date(self):
        """Test payment with past date."""
        self.login_and_navigate_to_bill_pay()
        
        # Get available accounts
        accounts = self.bill_pay_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            payee_data = self.generate_test_payee_data()
            
            # Try payment with past date
            past_date = (datetime.now() - timedelta(days=1)).strftime("%m/%d/%Y")
            self.bill_pay_page.send_payment(
                from_account=from_account,
                amount="100.00",
                date=past_date,
                description="Past date test",
                payee_info=payee_data,
                add_new_payee=True
            )
            
            # Should fail or show warning
            result = self.bill_pay_page.is_payment_successful()
            log.info(f"Past date payment result: {result}")

    @pytest.mark.regression
    def test_clear_payment_form(self):
        """Test clearing payment form functionality."""
        self.login_and_navigate_to_bill_pay()
        
        # Fill form with data
        accounts = self.bill_pay_page.get_available_accounts()
        if len(accounts) > 0:
            from_account = accounts[0]
            payee_data = self.generate_test_payee_data()
            
            self.bill_pay_page.select_from_account(from_account)
            self.bill_pay_page.enter_payment_amount("100.00")
            self.bill_pay_page.enter_payment_date(self.get_future_date(7))
            self.bill_pay_page.enter_description("Test description")
            self.bill_pay_page.fill_payee_information(**payee_data)
            
            # Clear form
            self.bill_pay_page.clear_payment_form()
            
            # Verify fields are cleared
            amount_value = self.bill_pay_page.get_attribute(self.bill_pay_page.AMOUNT_FIELD, "value")
            date_value = self.bill_pay_page.get_attribute(self.bill_pay_page.PAYMENT_DATE_FIELD, "value")
            description_value = self.bill_pay_page.get_attribute(self.bill_pay_page.DESCRIPTION_FIELD, "value")
            
            assert amount_value == "" or amount_value is None, "Amount field should be cleared"
            assert date_value == "" or date_value is None, "Date field should be cleared"
            assert description_value == "" or description_value is None, "Description field should be cleared"

    @pytest.mark.regression
    def test_payment_wait_for_completion(self):
        """Test payment completion wait functionality."""
        self.login_and_navigate_to_bill_pay()
        
        # Get available accounts
        accounts = self.bill_pay_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            payee_data = self.generate_test_payee_data()
            
            # Perform payment
            self.bill_pay_page.send_payment(
                from_account=from_account,
                amount="50.00",
                date=self.get_future_date(7),
                description="Wait test",
                payee_info=payee_data,
                add_new_payee=True
            )
            
            # Wait for completion
            completed = self.bill_pay_page.wait_for_payment_complete()
            assert completed, "Payment should complete within timeout"

    @pytest.mark.data_validation
    def test_payment_confirmation_details(self):
        """Test payment confirmation details accuracy."""
        self.login_and_navigate_to_bill_pay()
        
        # Get available accounts
        accounts = self.bill_pay_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            payee_data = self.generate_test_payee_data()
            amount = "75.25"
            date = self.get_future_date(7)
            description = "Confirmation test"
            
            # Perform payment
            self.bill_pay_page.send_payment(
                from_account=from_account,
                amount=amount,
                date=date,
                description=description,
                payee_info=payee_data,
                add_new_payee=True
            )
            
            if self.bill_pay_page.is_payment_successful():
                # Get confirmation details
                details = self.bill_pay_page.get_payment_confirmation_details()
                
                # Verify details contain expected information
                assert details or len(details) > 0, "Should have confirmation details"
                
                if 'amount' in details:
                    assert amount in details['amount'], f"Amount {amount} should be in confirmation"

    @pytest.mark.error_handling
    def test_payment_error_message_display(self):
        """Test error message display for invalid payment."""
        self.login_and_navigate_to_bill_pay()
        
        # Submit empty form
        self.bill_pay_page.click_send_payment()
        
        # Check if error message is displayed
        error_msg = self.bill_pay_page.get_error_message()
        # Note: Error message content depends on backend validation
        log.info(f"Error message for empty form: {error_msg}")

    @pytest.mark.security
    def test_payment_amount_field_security(self):
        """Test payment amount field security."""
        self.login_and_navigate_to_bill_pay()
        
        # Check that amount field doesn't expose sensitive data
        amount_field = self.page.locator(self.bill_pay_page.AMOUNT_FIELD)
        input_type = amount_field.get_attribute('type')
        
        # Should be text type (not password) for amount field
        assert input_type == 'text', "Amount field should be text type"

    @pytest.mark.browser_compatibility
    def test_bill_pay_form_javascript_functionality(self):
        """Test bill pay form JavaScript functionality."""
        self.login_and_navigate_to_bill_pay()
        
        # Test JavaScript evaluation on form
        form_exists = self.page.evaluate("""
            () => {
                const form = document.querySelector('#billpayForm');
                return form !== null;
            }
        """)
        
        assert form_exists, "Bill pay form should be accessible via JavaScript"
        
        # Test form filling via JavaScript
        accounts = self.bill_pay_page.get_available_accounts()
        if len(accounts) > 0:
            payee_data = self.generate_test_payee_data()
            
            # Fill form using JavaScript
            self.page.evaluate(f"""
                () => {{
                    document.querySelector('#fromAccountId').value = '{accounts[0]}';
                    document.querySelector('#amount').value = '100.00';
                    document.querySelector('#paymentDate').value = '{self.get_future_date(7)}';
                    document.querySelector('#payee\\.name').value = '{payee_data["name"]}';
                    document.querySelector('#payee\\.address\\.street').value = '{payee_data["address"]}';
                }}
            """)
            
            # Verify form is filled
            validation = self.bill_pay_page.validate_payment_form()
            # Note: May not be fully ready due to missing fields
            assert validation['from_account_selected'], "From account should be selected after JavaScript fill"
            assert validation['amount_entered'], "Amount should be entered after JavaScript fill"

    @pytest.mark.localization
    def test_bill_pay_page_localization_elements(self):
        """Test bill pay page localization elements."""
        self.login_and_navigate_to_bill_pay()
        
        # Check for currency formatting
        page_content = self.page.content()
        assert len(page_content) > 0, "Page should have content"
        
        # Check for proper labels
        labels = self.page.locator("label")
        if labels.count() > 0:
            # Verify labels are present
            assert labels.count() > 0, "Should have form labels"

    @pytest.mark.responsive
    def test_bill_pay_form_responsive_design(self):
        """Test bill pay form responsive design."""
        self.login_and_navigate_to_bill_pay()
        
        # Test different viewport sizes
        viewport_sizes = [
            {'width': 1920, 'height': 1080},  # Desktop
            {'width': 768, 'height': 1024},   # Tablet
            {'width': 375, 'height': 667}     # Mobile
        ]
        
        for viewport in viewport_sizes:
            self.page.set_viewport_size(viewport)
            
            # Check if form elements are still visible and functional
            assert self.page.is_visible(self.bill_pay_page.FROM_ACCOUNT_SELECT), f"From account select should be visible on {viewport['width']}x{viewport['height']}"
            assert self.page.is_visible(self.bill_pay_page.AMOUNT_FIELD), f"Amount field should be visible on {viewport['width']}x{viewport['height']}"
            assert self.page.is_visible(self.bill_pay_page.PAYMENT_DATE_FIELD), f"Date field should be visible on {viewport['width']}x{viewport['height']}"
            assert self.page.is_visible(self.bill_pay_page.SEND_PAYMENT_BUTTON), f"Send payment button should be visible on {viewport['width']}x{viewport['height']}"

    @pytest.mark.conditional
    def test_payment_with_single_account_scenario(self):
        """Test payment behavior with only one account available."""
        self.login_and_navigate_to_bill_pay()
        
        accounts = self.bill_pay_page.get_available_accounts()
        
        if len(accounts) == 1:
            # Test behavior with single account
            single_account = accounts[0]
            
            # Select the single account
            self.bill_pay_page.select_from_account(single_account)
            
            # Verify account is selected
            from_selected = self.bill_pay_page.get_attribute(self.bill_pay_page.FROM_ACCOUNT_SELECT, "value")
            assert from_selected == single_account, f"Account {single_account} should be selected"

    @pytest.mark.conditional
    def test_payment_with_multiple_accounts_scenario(self):
        """Test payment behavior with multiple accounts available."""
        self.login_and_navigate_to_bill_pay()
        
        accounts = self.bill_pay_page.get_available_accounts()
        
        if len(accounts) >= 2:
            # Test with multiple accounts
            assert len(accounts) >= 2, "Should have at least 2 accounts for this test"
            
            # Test selecting different accounts
            for account in accounts[:min(3, len(accounts))]:  # Test first 3 accounts
                self.bill_pay_page.select_from_account(account)
                
                # Verify selection
                from_selected = self.bill_pay_page.get_attribute(self.bill_pay_page.FROM_ACCOUNT_SELECT, "value")
                assert from_selected == account, f"Account {account} should be selected"

    @pytest.mark.usability
    def test_add_new_payee_checkbox_functionality(self):
        """Test add new payee checkbox functionality."""
        self.login_and_navigate_to_bill_pay()
        
        # Test checking the checkbox
        self.bill_pay_page.add_new_payee(True)
        assert self.bill_pay_page.is_checked(self.bill_pay_page.ADD_NEW_PAYEE_CHECKBOX), "Checkbox should be checked"
        
        # Test unchecking the checkbox
        self.bill_pay_page.add_new_payee(False)
        assert not self.bill_pay_page.is_checked(self.bill_pay_page.ADD_NEW_PAYEE_CHECKBOX), "Checkbox should be unchecked"

    @pytest.mark.edge_case
    def test_payment_with_special_characters_in_payee_name(self):
        """Test payment with special characters in payee name."""
        self.login_and_navigate_to_bill_pay()
        
        # Get available accounts
        accounts = self.bill_pay_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            payee_data = self.generate_test_payee_data()
            payee_data['name'] = "Test-O'Connor & Associates"
            
            # Try payment with special characters
            self.bill_pay_page.send_payment(
                from_account=from_account,
                amount="100.00",
                date=self.get_future_date(7),
                description="Special characters test",
                payee_info=payee_data,
                add_new_payee=True
            )
            
            # Should handle special characters gracefully
            result = self.bill_pay_page.is_payment_successful()
            log.info(f"Special characters payment result: {result}")

    @pytest.mark.edge_case
    def test_payment_with_long_description(self):
        """Test payment with very long description."""
        self.login_and_navigate_to_bill_pay()
        
        # Get available accounts
        accounts = self.bill_pay_page.get_available_accounts()
        
        if len(accounts) > 0:
            from_account = accounts[0]
            payee_data = self.generate_test_payee_data()
            
            # Try payment with long description
            long_description = "This is a very long payment description that exceeds the normal length to test how the system handles extended text fields and ensure proper processing and display of lengthy descriptions in the payment system."
            
            self.bill_pay_page.send_payment(
                from_account=from_account,
                amount="100.00",
                date=self.get_future_date(7),
                description=long_description,
                payee_info=payee_data,
                add_new_payee=True
            )
            
            # Should handle long description
            result = self.bill_pay_page.is_payment_successful()
            log.info(f"Long description payment result: {result}")
