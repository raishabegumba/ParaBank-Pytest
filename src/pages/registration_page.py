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
    # ParaBank inputs do not always have stable aria-label/label bindings,
    # so tests may only be satisfied by placeholder/text presence.
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
        # Use the same base URL pattern as the rest of the framework.
        self.goto("https://parabank.parasoft.com/parabank/register.htm?ConnType=JDBC")
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

    # def is_registration_successful(self) -> bool:
    #     """Check if registration was successful.

    #     ParaBank typically shows:
    #     - a success header (#rightPanel h1) when registration completes
    #     - or a validation/error state (".error" and/or missing required fields)

    #     We only treat registration as successful if we see the expected success
    #     wording AND no error message is currently visible.
    #     """
    #     try:
    #         # If backend validation failed, an .error element is often present.
    #         if self.is_visible(self.ERROR_MESSAGE, timeout=1000):
    #             return False

    #         self.wait_helper.wait_for_element(
    #             self.SUCCESS_MESSAGE,
    #             WaitStrategy.ELEMENT_VISIBLE,
    #             timeout=5000,
    #         )
    #         success_text = (self.get_text(self.SUCCESS_MESSAGE) or "").strip().lower()

    #         # Accept the common success header.
    #         if "signing up is easy" in success_text:
    #             # Only consider it real success if no error is present.
    #             return True

    #         # Some builds show a welcome/account created message.
    #         if "welcome" in success_text and "account" in success_text:
    #             return True

    #         return False
    #     except:
    #         return False


    def is_registration_successful(self) -> bool:
        """Check if registration was successful."""
        try:
            # If error exists, registration failed
            if self.is_visible(self.ERROR_MESSAGE, timeout=1000):
                return False

        # Wait for success message
            self.wait_helper.wait_for_element(
                self.SUCCESS_MESSAGE,
                WaitStrategy.ELEMENT_VISIBLE,
                timeout=5000,
            )

            success_text = (
                self.get_text(self.SUCCESS_MESSAGE) or ""
                ).strip().lower()

            log.info(f"Registration success text: {success_text}")

            # ParaBank success page usually shows:
            # "Welcome username"
            return "welcome" in success_text

        except Exception as e:
            log.error(f"Registration success check failed: {e}")
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
            password = self.get_attribute(self.PASSWORD_FIELD, "value")
            if password is None:
                password = self.page.locator(self.PASSWORD_FIELD).input_value()
            confirm_password = self.get_attribute(self.CONFIRM_PASSWORD_FIELD, "value")
            if confirm_password is None:
                confirm_password = self.page.locator(self.CONFIRM_PASSWORD_FIELD).input_value()
            password = password or ""
            confirm_password = confirm_password or ""
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
                # Some ParaBank builds don't update the DOM 'value' attribute immediately,
                # but the typed value is reflected in input value/state.
                value = self.get_attribute(selector, "value")
                if value is None:
                    value = self.page.locator(selector).input_value()
                value = value or ""
                validation_results[field_name] = bool(str(value).strip())
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
        """Assert that registration was successful.

        Keep success assertions aligned with `is_registration_successful()`
        because ParaBank wording can differ across environments/builds.
        """
        self.assert_helper.assert_element_visible(self.SUCCESS_MESSAGE)
        success_text = self.get_text(self.SUCCESS_MESSAGE).strip()
        success_ok = self.is_registration_successful()
        assert success_ok, f"Registration success not detected. Actual success header: {success_text!r}"

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
        
        NOTE: These are *static* checks used by tests after filling the form.
        We read values using Playwright's `input_value()` when `value` attribute is missing.
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
            zip_code = self.get_attribute(self.ZIP_CODE_FIELD, "value")
            if zip_code is None:
                zip_code = self.page.locator(self.ZIP_CODE_FIELD).input_value()
            zip_code = zip_code or ""

            # Tests expect strict 5-digit ZIP validation.
            constraints['zip_code_valid'] = zip_code.isdigit() and len(zip_code) == 5
            
            # Phone validation (basic 10-digit check)
            phone = self.get_attribute(self.PHONE_FIELD, "value")
            if phone is None:
                phone = self.page.locator(self.PHONE_FIELD).input_value()
            phone = phone or ""

            phone_digits = ''.join(filter(str.isdigit, phone))
            # ParaBank accepts formatted phone strings like 555-123-4567.
            # Tests expect:
            # - minimum 10 digits
            # - error on non-digit characters not in valid separators
            phone_raw = phone
            phone_stripped = phone_raw.strip()

            # Allow digits, spaces, and the common separators '-' and '/'.
            import re
            if not re.fullmatch(r"[0-9\-\s/()]+", phone_stripped):
                constraints['phone_valid'] = False
            else:
                constraints['phone_valid'] = len(phone_digits) >= 10
            
            # SSN validation (basic 9-digit check)
            ssn = self.get_attribute(self.SSN_FIELD, "value")
            if ssn is None:
                ssn = self.page.locator(self.SSN_FIELD).input_value()
            ssn = ssn or ""

            ssn_digits = ''.join(filter(str.isdigit, ssn))
            constraints['ssn_valid'] = len(ssn_digits) == 9
            
            # Username length validation
            # username = self.get_attribute(self.USERNAME_FIELD, "value") or ""
            username = self.get_attribute(self.USERNAME_FIELD, "value")
            if username is None:
                username = self.page.locator(self.USERNAME_FIELD).input_value()
            username = username or ""
            # Tests expect min 3 chars and max 50 chars.
            constraints['username_length_valid'] = 3 <= len(username) <= 50
            
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
