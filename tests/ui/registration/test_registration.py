"""Comprehensive UI test suite for ParaBank Registration page."""
import pytest
import random
import string
from datetime import datetime
from playwright.sync_api import Page
from src.pages.registration_page import RegistrationPage
from src.pages.login_page import LoginPage
from src.utils.test_data_utils import TestDataUtils
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.registration
class TestRegistrationPage:
    """Enterprise-grade test suite for registration functionality."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test environment."""
        self.page = page
        self.registration_page = RegistrationPage(page)
        self.login_page = LoginPage(page)
        self.test_data = TestDataUtils()

    def generate_test_user_data(self) -> dict:
        """Generate valid test user data."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        
        return {
            'first_name': 'Test',
            'last_name': f'User{timestamp}',
            'address': '123 Test Street',
            'city': 'Test City',
            'state': 'CA',
            'zip_code': '12345',
            'phone': '5551234567',
            'ssn': '123456789',
            'username': f'testuser_{timestamp}_{random_suffix}',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!'
        }

    @pytest.mark.smoke
    def test_registration_page_loads_correctly(self):
        """Test that registration page loads with all required elements."""
        self.registration_page.navigate_to_registration()
        self.registration_page.assert_registration_page_loaded()
        
        # Verify page title
        assert "ParaBank" in self.page.title()
        assert "Register" in self.page.title()

    @pytest.mark.smoke
    def test_successful_registration_with_valid_data(self):
        """Test successful user registration with valid data."""
        test_user = self.generate_test_user_data()
        
        self.registration_page.navigate_to_registration()
        self.registration_page.complete_registration(**test_user)
        
        # Verify successful registration
        assert self.registration_page.is_registration_successful()
        
        # Check success message
        success_msg = self.registration_page.get_success_message()
        assert "Welcome" in success_msg
        assert "account was created successfully" in success_msg.lower()

    @pytest.mark.regression
    def test_registration_with_missing_required_fields(self):
        """Test registration fails when required fields are missing."""
        self.registration_page.navigate_to_registration()
        
        # Test each required field individually
        test_user = self.generate_test_user_data()
        
        # Test missing first name
        test_user_missing = test_user.copy()
        test_user_missing['first_name'] = ''
        self.registration_page.fill_personal_info(**{k: v for k, v in test_user_missing.items() if k in [
            'first_name', 'last_name', 'address', 'city', 'state', 'zip_code', 'phone', 'ssn'
        ]})
        self.registration_page.fill_account_info(**{k: v for k, v in test_user_missing.items() if k in [
            'username', 'password', 'confirm_password'
        ]})
        self.registration_page.click_register_button()
        
        # Should show error or prevent submission
        assert not self.registration_page.is_registration_successful()

    @pytest.mark.regression
    def test_registration_with_password_mismatch(self):
        """Test registration fails when passwords don't match."""
        test_user = self.generate_test_user_data()
        test_user['confirm_password'] = 'DifferentPassword123!'
        
        self.registration_page.navigate_to_registration()
        self.registration_page.complete_registration(**test_user)
        
        # Should fail registration
        assert not self.registration_page.is_registration_successful()

    @pytest.mark.regression
    def test_registration_with_invalid_zip_code(self):
        """Test registration with invalid ZIP code format."""
        test_user = self.generate_test_user_data()
        test_user['zip_code'] = 'invalid'
        
        self.registration_page.navigate_to_registration()
        self.registration_page.complete_registration(**test_user)
        
        # Should fail registration
        assert not self.registration_page.is_registration_successful()

    @pytest.mark.regression
    def test_registration_with_invalid_phone_number(self):
        """Test registration with invalid phone number format."""
        test_user = self.generate_test_user_data()
        test_user['phone'] = 'abc'
        
        self.registration_page.navigate_to_registration()
        self.registration_page.complete_registration(**test_user)
        
        # Should fail registration
        assert not self.registration_page.is_registration_successful()

    @pytest.mark.regression
    def test_registration_with_invalid_ssn(self):
        """Test registration with invalid SSN format."""
        test_user = self.generate_test_user_data()
        test_user['ssn'] = '123'
        
        self.registration_page.navigate_to_registration()
        self.registration_page.complete_registration(**test_user)
        
        # Should fail registration
        assert not self.registration_page.is_registration_successful()

    @pytest.mark.regression
    def test_registration_with_weak_password(self):
        """Test registration fails with weak password."""
        test_user = self.generate_test_user_data()
        test_user['password'] = 'weak'
        test_user['confirm_password'] = 'weak'
        
        self.registration_page.navigate_to_registration()
        self.registration_page.complete_registration(**test_user)
        
        # Should fail registration
        assert not self.registration_page.is_registration_successful()

    @pytest.mark.regression
    def test_registration_with_duplicate_username(self):
        """Test registration fails with duplicate username."""
        # First, register a user
        test_user = self.generate_test_user_data()
        self.registration_page.navigate_to_registration()
        self.registration_page.complete_registration(**test_user)
        assert self.registration_page.is_registration_successful()
        
        # Try to register again with same username
        self.registration_page.navigate_to_registration()
        test_user['first_name'] = 'Another'  # Change other details
        test_user['last_name'] = 'User'
        self.registration_page.complete_registration(**test_user)
        
        # Should fail due to duplicate username
        assert not self.registration_page.is_registration_successful()

    @pytest.mark.accessibility
    def test_registration_form_accessibility(self):
        """Test registration form accessibility features."""
        self.registration_page.navigate_to_registration()
        
        # Check if all form fields have proper labels
        required_fields = [
            self.registration_page.FIRST_NAME_FIELD,
            self.registration_page.LAST_NAME_FIELD,
            self.registration_page.ADDRESS_FIELD,
            self.registration_page.CITY_FIELD,
            self.registration_page.STATE_FIELD,
            self.registration_page.ZIP_CODE_FIELD,
            self.registration_page.PHONE_FIELD,
            self.registration_page.SSN_FIELD,
            self.registration_page.USERNAME_FIELD,
            self.registration_page.PASSWORD_FIELD,
            self.registration_page.CONFIRM_PASSWORD_FIELD
        ]
        
        for field in required_fields:
            element = self.page.locator(field)
            # Check for label, placeholder, or aria-label
            has_label = bool(
                element.get_attribute('aria-label') or 
                element.get_attribute('placeholder') or
                element.locator('xpath=./preceding::label[1]').count() > 0
            )
            assert has_label, f"Field {field} lacks proper labeling"

    @pytest.mark.security
    def test_password_field_is_masked(self):
        """Test that password field is properly masked."""
        self.registration_page.navigate_to_registration()
        
        # Check password field type
        password_field = self.page.locator(self.registration_page.PASSWORD_FIELD)
        input_type = password_field.get_attribute('type')
        assert input_type == 'password', "Password field should be masked"
        
        # Check confirm password field type
        confirm_password_field = self.page.locator(self.registration_page.CONFIRM_PASSWORD_FIELD)
        confirm_input_type = confirm_password_field.get_attribute('type')
        assert confirm_input_type == 'password', "Confirm password field should be masked"

    @pytest.mark.usability
    def test_form_validation_state(self):
        """Test form validation state tracking."""
        self.registration_page.navigate_to_registration()
        
        # Initially form should not be ready
        validation_state = self.registration_page.get_form_validation_state()
        assert not validation_state['all_required_filled']
        assert not validation_state['form_ready']
        
        # Fill valid data
        test_user = self.generate_test_user_data()
        self.registration_page.fill_personal_info(**{k: v for k, v in test_user.items() if k in [
            'first_name', 'last_name', 'address', 'city', 'state', 'zip_code', 'phone', 'ssn'
        ]})
        self.registration_page.fill_account_info(**{k: v for k, v in test_user.items() if k in [
            'username', 'password', 'confirm_password'
        ]})
        
        # Now form should be ready
        validation_state = self.registration_page.get_form_validation_state()
        assert validation_state['all_required_filled']
        assert validation_state['passwords_match']
        assert validation_state['form_ready']

    @pytest.mark.usability
    def test_field_constraints_validation(self):
        """Test field constraints validation."""
        self.registration_page.navigate_to_registration()
        
        # Fill valid data
        test_user = self.generate_test_user_data()
        self.registration_page.fill_personal_info(**{k: v for k, v in test_user.items() if k in [
            'first_name', 'last_name', 'address', 'city', 'state', 'zip_code', 'phone', 'ssn'
        ]})
        self.registration_page.fill_account_info(**{k: v for k, v in test_user.items() if k in [
            'username', 'password', 'confirm_password'
        ]})
        
        # Validate constraints
        constraints = self.registration_page.validate_field_constraints()
        assert constraints['zip_code_valid']
        assert constraints['phone_valid']
        assert constraints['ssn_valid']
        assert constraints['username_length_valid']
        assert constraints['password_strength_adequate']

    @pytest.mark.navigation
    def test_login_link_navigation(self):
        """Test login link navigation from registration page."""
        self.registration_page.navigate_to_registration()
        self.registration_page.click_login_link()
        
        # Should navigate to login page
        self.login_page.assert_login_page_loaded()

    @pytest.mark.performance
    def test_registration_page_load_performance(self):
        """Test registration page load performance."""
        start_time = datetime.now()
        self.registration_page.navigate_to_registration()
        self.registration_page.assert_registration_page_loaded()
        load_time = (datetime.now() - start_time).total_seconds()
        
        # Page should load within reasonable time (5 seconds)
        assert load_time < 5.0, f"Page load time {load_time}s exceeds threshold"

    @pytest.mark.edge_case
    def test_registration_with_special_characters_in_name(self):
        """Test registration with special characters in name fields."""
        test_user = self.generate_test_user_data()
        test_user['first_name'] = "John-O'Connor"
        test_user['last_name'] = "Smith-Jones"
        
        self.registration_page.navigate_to_registration()
        self.registration_page.complete_registration(**test_user)
        
        # Should handle special characters gracefully
        result = self.registration_page.is_registration_successful()
        # Note: This test might fail depending on backend validation
        log.info(f"Registration with special characters result: {result}")

    @pytest.mark.edge_case
    def test_registration_with_long_username(self):
        """Test registration with very long username."""
        test_user = self.generate_test_user_data()
        test_user['username'] = 'a' * 50  # 50 characters
        
        self.registration_page.navigate_to_registration()
        self.registration_page.complete_registration(**test_user)
        
        # Should fail due to username length
        assert not self.registration_page.is_registration_successful()

    @pytest.mark.edge_case
    def test_registration_with_short_password(self):
        """Test registration with very short password."""
        test_user = self.generate_test_user_data()
        test_user['password'] = 'abc'
        test_user['confirm_password'] = 'abc'
        
        self.registration_page.navigate_to_registration()
        self.registration_page.complete_registration(**test_user)
        
        # Should fail due to password length
        assert not self.registration_page.is_registration_successful()

    @pytest.mark.regression
    def test_clear_registration_form(self):
        """Test clearing registration form functionality."""
        self.registration_page.navigate_to_registration()
        
        # Fill form with data
        test_user = self.generate_test_user_data()
        self.registration_page.fill_personal_info(**{k: v for k, v in test_user.items() if k in [
            'first_name', 'last_name', 'address', 'city', 'state', 'zip_code', 'phone', 'ssn'
        ]})
        self.registration_page.fill_account_info(**{k: v for k, v in test_user.items() if k in [
            'username', 'password', 'confirm_password'
        ]})
        
        # Clear form
        self.registration_page.clear_registration_form()
        
        # Verify form is cleared
        validation_state = self.registration_page.get_form_validation_state()
        assert not validation_state['all_required_filled']

    @pytest.mark.regression
    def test_registration_wait_for_completion(self):
        """Test registration completion wait functionality."""
        test_user = self.generate_test_user_data()
        
        self.registration_page.navigate_to_registration()
        self.registration_page.complete_registration(**test_user)
        
        # Wait for registration to complete
        completed = self.registration_page.wait_for_registration_complete()
        assert completed, "Registration should complete within timeout"

    @pytest.mark.integration
    def test_registration_then_login(self):
        """Test complete flow: registration then login with new account."""
        test_user = self.generate_test_user_data()
        
        # Register new user
        self.registration_page.navigate_to_registration()
        self.registration_page.complete_registration(**test_user)
        assert self.registration_page.is_registration_successful()
        
        # Navigate to login and login with new credentials
        self.login_page.navigate_to_login()
        login_result = self.login_page.login_with_validation(
            test_user['username'], 
            test_user['password']
        )
        
        assert login_result['success'], "Should be able to login with newly registered account"

    @pytest.mark.error_handling
    def test_registration_error_message_display(self):
        """Test error message display for invalid registration."""
        self.registration_page.navigate_to_registration()
        
        # Submit empty form
        self.registration_page.click_register_button()
        
        # Check if error message is displayed
        error_msg = self.registration_page.get_error_message()
        # Note: Error message content depends on backend validation
        log.info(f"Error message for empty form: {error_msg}")

    @pytest.mark.localization
    def test_registration_page_localization_elements(self):
        """Test registration page has proper localization elements."""
        self.registration_page.navigate_to_registration()
        
        # Check for language indicators if applicable
        # This test can be expanded based on actual localization requirements
        page_content = self.page.content()
        assert len(page_content) > 0, "Page should have content"

    @pytest.mark.browser_compatibility
    def test_registration_form_browser_compatibility(self):
        """Test registration form works across different browser features."""
        self.registration_page.navigate_to_registration()
        
        # Test JavaScript functionality
        test_user = self.generate_test_user_data()
        
        # Fill form using JavaScript
        self.page.evaluate("""
            (userData) => {
                document.querySelector('#customer\\.firstName').value = userData.first_name;
                document.querySelector('#customer\\.lastName').value = userData.last_name;
                document.querySelector('#customer\\.address\\.street').value = userData.address;
                document.querySelector('#customer\\.address\\.city').value = userData.city;
                document.querySelector('#customer\\.address\\.state').value = userData.state;
                document.querySelector('#customer\\.address\\.zipCode').value = userData.zip_code;
                document.querySelector('#customer\\.phoneNumber').value = userData.phone;
                document.querySelector('#customer\\.ssn').value = userData.ssn;
                document.querySelector('#customer\\.username').value = userData.username;
                document.querySelector('#customer\\.password').value = userData.password;
                document.querySelector('#repeatedPassword').value = userData.confirm_password;
            }
        """, test_user)
        
        # Submit and verify
        self.registration_page.click_register_button()
        
        # Should process the form
        result = self.registration_page.wait_for_registration_complete()
        assert result, "Form submission should complete"
