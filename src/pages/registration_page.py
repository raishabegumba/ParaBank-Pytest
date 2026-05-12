"""ParaBank Registration Page Object Model."""
from typing import Optional, Dict, Any
from playwright.sync_api import Page
from src.pages.base_page import BasePage
from src.utils.wait_helpers import WaitHelper, WaitStrategy
from src.utils.assertion_helpers import AssertionHelper
from src.utils.retry_handler import retry_with_backoff
from src.config.logger import log


class RegistrationPage(BasePage):
    """Enterprise-grade Registration page object for ParaBank."""

    # Locators (using escaped CSS selectors for ParaBank)
    FIRST_NAME_FIELD = "#customer\\.firstName"
    LAST_NAME_FIELD = "#customer\\.lastName"
    ADDRESS_FIELD = "#customer\\.address\\.street"
    CITY_FIELD = "#customer\\.address\\.city"
    STATE_FIELD = "#customer\\.address\\.state"
    ZIP_CODE_FIELD = "#customer\\.address\\.zipCode"
    PHONE_FIELD = "#customer\\.phoneNumber"
    SSN_FIELD = "#customer\\.ssn"
    USERNAME_FIELD = "#customer\\.username"
    PASSWORD_FIELD = "#customer\\.password"
    CONFIRM_PASSWORD_FIELD = "#repeatedPassword"
    REGISTER_BUTTON = "input[type='submit'][value='Register']"
    SUCCESS_MESSAGE = "#rightPanel h1"
    ERROR_MESSAGE = ".error"
    LOGIN_LINK = "a[href*='index.htm']"
    REGISTRATION_FORM = "#customerForm"

    def __init__(self, page: Page):
        """Initialize Registration page with enterprise features."""
        super().__init__(page)
        self.wait_helper = WaitHelper(page)
        self.assert_helper = AssertionHelper(page)
        self.page_url = "parabank/register.htm"

    @retry_with_backoff(max_attempts=3, base_delay=0.5)
    def navigate_to_registration(self) -> None:
        """Navigate to registration page with retry mechanism."""
        self.goto("https://parabank.parasoft.com/parabank/register.htm")
        self.assert_helper.assert_element_visible(self.FIRST_NAME_FIELD)
        self.assert_helper.assert_element_visible(self.LAST_NAME_FIELD)
        log.info("Successfully navigated to registration page")

    def fill_personal_info(
        self,
        first_name: str,
        last_name: str,
        address: str,
        city: str,
        state: str,
        zip_code: str,
        phone: str,
        ssn: str
    ) -> None:
        """
        Fill personal information fields.
        
        Args:
            first_name: First name
            last_name: Last name
            address: Street address
            city: City
            state: State
            zip_code: ZIP code
            phone: Phone number
            ssn: Social Security Number
        """
        self.wait_helper.wait_for_element(self.FIRST_NAME_FIELD, WaitStrategy.ELEMENT_VISIBLE)
        
        self.fill(self.FIRST_NAME_FIELD, first_name)
        self.fill(self.LAST_NAME_FIELD, last_name)
        self.fill(self.ADDRESS_FIELD, address)
        self.fill(self.CITY_FIELD, city)
        self.fill(self.STATE_FIELD, state)
        self.fill(self.ZIP_CODE_FIELD, zip_code)
        self.fill(self.PHONE_FIELD, phone)
        self.fill(self.SSN_FIELD, ssn)
        
        log.info(f"Filled personal information for: {first_name} {last_name}")

    def fill_account_info(
        self,
        username: str,
        password: str,
        confirm_password: str
    ) -> None:
        """
        Fill account information fields.
        
        Args:
            username: Username
            password: Password
            confirm_password: Confirm password
        """
        self.wait_helper.wait_for_element(self.USERNAME_FIELD, WaitStrategy.ELEMENT_VISIBLE)
        
        self.fill(self.USERNAME_FIELD, username)
        self.fill(self.PASSWORD_FIELD, password)
        self.fill(self.CONFIRM_PASSWORD_FIELD, confirm_password)
        
        log.info(f"Filled account information for username: {username}")

    def complete_registration(
        self,
        first_name: str,
        last_name: str,
        address: str,
        city: str,
        state: str,
        zip_code: str,
        phone: str,
        ssn: str,
        username: str,
        password: str,
        confirm_password: str
    ) -> None:
        """
        Complete full registration form.
        
        Args:
            All registration fields
        """
        try:
            self.fill_personal_info(
                first_name, last_name, address, city, state, zip_code, phone, ssn
            )
            self.fill_account_info(username, password, confirm_password)
            self.click_register_button()
            log.info("Registration form completed and submitted")
        except Exception as e:
            log.error(f"Registration failed: {e}")
            raise

    def click_register_button(self) -> None:
        """Click register button."""
        self.wait_helper.wait_for_element(self.REGISTER_BUTTON, WaitStrategy.ELEMENT_CLICKABLE)
        self.click(self.REGISTER_BUTTON)
        log.info("Clicked register button")

    def is_registration_successful(self) -> bool:
        """Check if registration was successful."""
        try:
            self.wait_helper.wait_for_element(self.SUCCESS_MESSAGE, WaitStrategy.ELEMENT_VISIBLE, timeout=5000)
            success_text = self.get_text(self.SUCCESS_MESSAGE)
            return "Welcome" in success_text and "Your account was created successfully" in success_text
        except:
            return False

    def get_success_message(self) -> str:
        """Get success message after registration."""
        try:
            if self.is_visible(self.SUCCESS_MESSAGE, timeout=5000):
                return self.get_text(self.SUCCESS_MESSAGE)
            return ""
        except:
            return ""

    def get_error_message(self) -> str:
        """Get error message from registration attempt."""
        try:
            if self.is_visible(self.ERROR_MESSAGE, timeout=3000):
                return self.get_text(self.ERROR_MESSAGE)
            return ""
        except:
            return ""

    def is_username_available(self, username: str) -> bool:
        """
        Check if username is available by attempting to fill and checking for validation.
        
        Args:
            username: Username to check
            
        Returns:
            True if username appears available
        """
        try:
            self.fill(self.USERNAME_FIELD, username)
            # Check for immediate validation messages
            self.page.wait_for_timeout(1000)  # Brief wait for validation
            
            error_text = self.get_error_message()
            return not any(phrase in error_text.lower() for phrase in ['already exists', 'taken', 'unavailable'])
        except:
            return False

    def validate_password_match(self) -> bool:
        """Check if password and confirm password fields match."""
        try:
            password = self.get_attribute(self.PASSWORD_FIELD, "value") or ""
            confirm_password = self.get_attribute(self.CONFIRM_PASSWORD_FIELD, "value") or ""
            return password == confirm_password
        except:
            return False

    def validate_required_fields(self) -> Dict[str, bool]:
        """
        Validate all required fields are filled.
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {}
        required_fields = {
            'first_name': self.FIRST_NAME_FIELD,
            'last_name': self.LAST_NAME_FIELD,
            'address': self.ADDRESS_FIELD,
            'city': self.CITY_FIELD,
            'state': self.STATE_FIELD,
            'zip_code': self.ZIP_CODE_FIELD,
            'phone': self.PHONE_FIELD,
            'ssn': self.SSN_FIELD,
            'username': self.USERNAME_FIELD,
            'password': self.PASSWORD_FIELD,
            'confirm_password': self.CONFIRM_PASSWORD_FIELD
        }
        
        for field_name, selector in required_fields.items():
            try:
                value = self.get_attribute(selector, "value") or ""
                validation_results[field_name] = bool(value.strip())
            except:
                validation_results[field_name] = False
        
        return validation_results

    def clear_registration_form(self) -> None:
        """Clear all registration form fields."""
        fields = [
            self.FIRST_NAME_FIELD, self.LAST_NAME_FIELD, self.ADDRESS_FIELD,
            self.CITY_FIELD, self.STATE_FIELD, self.ZIP_CODE_FIELD,
            self.PHONE_FIELD, self.SSN_FIELD, self.USERNAME_FIELD,
            self.PASSWORD_FIELD, self.CONFIRM_PASSWORD_FIELD
        ]
        
        for field in fields:
            self.fill(field, "")
        
        log.info("Cleared registration form")

    def click_login_link(self) -> None:
        """Click login link to navigate back to login page."""
        self.wait_helper.wait_for_and_click(self.LOGIN_LINK)
        log.info("Clicked login link")

    def assert_registration_page_loaded(self) -> None:
        """Assert that registration page is properly loaded."""
        required_elements = [
            self.FIRST_NAME_FIELD, self.LAST_NAME_FIELD, self.ADDRESS_FIELD,
            self.CITY_FIELD, self.STATE_FIELD, self.ZIP_CODE_FIELD,
            self.PHONE_FIELD, self.SSN_FIELD, self.USERNAME_FIELD,
            self.PASSWORD_FIELD, self.CONFIRM_PASSWORD_FIELD, self.REGISTER_BUTTON
        ]
        
        for element in required_elements:
            self.assert_helper.assert_element_visible(element)
        
        self.assert_helper.assert_element_is_clickable(self.REGISTER_BUTTON)
        log.info("Registration page loaded successfully")

    def assert_registration_successful(self) -> None:
        """Assert that registration was successful."""
        self.assert_helper.assert_element_visible(self.SUCCESS_MESSAGE)
        success_text = self.get_text(self.SUCCESS_MESSAGE)
        assert "Welcome" in success_text, "Welcome message not found"
        assert "account was created successfully" in success_text.lower(), "Success message not found"
        log.info("Registration success assertion verified")

    def assert_registration_failed(self, expected_error: Optional[str] = None) -> None:
        """Assert that registration failed with expected error."""
        self.assert_helper.assert_element_visible(self.ERROR_MESSAGE)
        
        if expected_error:
            self.assert_helper.assert_element_contains_text(self.ERROR_MESSAGE, expected_error)
        
        log.info("Registration failure assertion verified")

    def get_form_validation_state(self) -> Dict[str, Any]:
        """Get current form validation state."""
        validation_state = {
            'all_required_filled': False,
            'passwords_match': False,
            'username_available': False,
            'form_ready': False
        }
        
        try:
            # Check required fields
            required_validation = self.validate_required_fields()
            validation_state['all_required_filled'] = all(required_validation.values())
            
            # Check password match
            validation_state['passwords_match'] = self.validate_password_match()
            
            # Check username availability (basic check)
            username = self.get_attribute(self.USERNAME_FIELD, "value") or ""
            if username:
                validation_state['username_available'] = self.is_username_available(username)
            
            # Overall form readiness
            validation_state['form_ready'] = (
                validation_state['all_required_filled'] and
                validation_state['passwords_match']
            )
            
        except Exception as e:
            log.error(f"Form validation state check failed: {e}")
        
        return validation_state

    def validate_field_constraints(self) -> Dict[str, Any]:
        """
        Validate field constraints and business rules.
        
        Returns:
            Dictionary with constraint validation results
        """
        constraints = {
            'zip_code_valid': False,
            'phone_valid': False,
            'ssn_valid': False,
            'username_length_valid': False,
            'password_strength_adequate': False
        }
        
        try:
            # ZIP code validation (basic 5-digit check)
            zip_code = self.get_attribute(self.ZIP_CODE_FIELD, "value") or ""
            constraints['zip_code_valid'] = zip_code.isdigit() and len(zip_code) == 5
            
            # Phone validation (basic 10-digit check)
            phone = self.get_attribute(self.PHONE_FIELD, "value") or ""
            phone_digits = ''.join(filter(str.isdigit, phone))
            constraints['phone_valid'] = len(phone_digits) >= 10
            
            # SSN validation (basic 9-digit check)
            ssn = self.get_attribute(self.SSN_FIELD, "value") or ""
            ssn_digits = ''.join(filter(str.isdigit, ssn))
            constraints['ssn_valid'] = len(ssn_digits) == 9
            
            # Username length validation
            username = self.get_attribute(self.USERNAME_FIELD, "value") or ""
            constraints['username_length_valid'] = 3 <= len(username) <= 20
            
            # Password strength (basic checks)
            password = self.get_attribute(self.PASSWORD_FIELD, "value") or ""
            constraints['password_strength_adequate'] = (
                len(password) >= 8 and
                any(c.isupper() for c in password) and
                any(c.islower() for c in password) and
                any(c.isdigit() for c in password)
            )
            
        except Exception as e:
            log.error(f"Field constraints validation failed: {e}")
        
        return constraints

    def wait_for_registration_complete(self, timeout: int = 10000) -> bool:
        """Wait for registration process to complete."""
        try:
            return self.wait_helper.wait_for_custom_condition(
                condition=lambda: (
                    self.is_visible(self.SUCCESS_MESSAGE, timeout=1000) or 
                    self.is_visible(self.ERROR_MESSAGE, timeout=1000)
                ),
                timeout=timeout,
                message="Registration completion timeout"
            )
        except:
            return False
