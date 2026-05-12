"""ParaBank Login Page Object Model."""
from typing import Optional, Dict, Any
from playwright.sync_api import Page
from src.pages.base_page import BasePage
from src.utils.wait_helpers import WaitHelper, WaitStrategy
from src.utils.assertion_helpers import AssertionHelper
from src.utils.retry_handler import retry_with_backoff
from src.config.logger import log


class LoginPage(BasePage):
    """Enterprise-grade Login page object for ParaBank."""

    # Locators (CSS Selectors)
    USERNAME_FIELD = ".login input[name='username']"
    PASSWORD_FIELD = ".login input[name='password']"
    LOGIN_BUTTON = ".login input[type='submit'][value='Log In']"
    ERROR_MESSAGE = ".error"
    SUCCESS_MESSAGE = ".success"
    WELCOME_MESSAGE = "#rightPanel h1"
    FORGOT_PASSWORD_LINK = "a[href='lookup.htm']"
    REGISTER_LINK = "a[href*='register.htm']"
    ACCOUNTS_OVERVIEW_LINK = "a[href*='overview.htm']"
    LOGIN_FORM = "#loginPanel form"
    
    def __init__(self, page: Page):
        """Initialize Login page with enterprise features."""
        super().__init__(page)
        self.wait_helper = WaitHelper(page)
        self.assert_helper = AssertionHelper(page)
        self.page_url = "parabank/index.htm"

    @retry_with_backoff(max_attempts=3, base_delay=0.5)
    def navigate_to_login(self) -> None:
        """Navigate to login page with retry mechanism."""
        self.goto("https://parabank.parasoft.com/parabank/index.htm?ConnType=JDBC")
        self.assert_helper.assert_element_visible(self.USERNAME_FIELD)
        self.assert_helper.assert_element_visible(self.PASSWORD_FIELD)
        log.info("Successfully navigated to login page")

    def enter_username(self, username: str, clear_first: bool = True) -> None:
        """
        Enter username with validation.
        
        Args:
            username: Username to enter
            clear_first: Clear field before entering
        """
        self.wait_helper.wait_for_element(self.USERNAME_FIELD, WaitStrategy.ELEMENT_VISIBLE)
        if clear_first:
            self.page.locator(self.USERNAME_FIELD).clear()
        self.fill(self.USERNAME_FIELD, username)
        log.info(f"Entered username: {username}")

    def enter_password(self, password: str, clear_first: bool = True) -> None:
        """
        Enter password with validation.
        
        Args:
            password: Password to enter
            clear_first: Clear field before entering
        """
        self.wait_helper.wait_for_element(self.PASSWORD_FIELD, WaitStrategy.ELEMENT_VISIBLE)
        if clear_first:
            self.page.locator(self.PASSWORD_FIELD).clear()
        self.fill(self.PASSWORD_FIELD, password)
        log.info("Entered password")

    def click_login(self) -> None:
        """Click login button with validation."""
        self.wait_helper.wait_for_element(self.LOGIN_BUTTON, WaitStrategy.ELEMENT_CLICKABLE)
        self.click(self.LOGIN_BUTTON)
        log.info("Clicked login button")

    @retry_with_backoff(max_attempts=2, base_delay=1.0)
    def login(self, username: str, password: str) -> None:
        """
        Perform complete login action with validation.
        
        Args:
            username: Login username
            password: Login password
        """
        try:
            self.enter_username(username)
            self.enter_password(password)
            self.click_login()
            log.info(f"Login attempted for user: {username}")
        except Exception as e:
            log.error(f"Login failed: {e}")
            raise

    def login_with_validation(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login with comprehensive validation and return results.
        
        Args:
            username: Login username
            password: Login password
            
        Returns:
            Dictionary with login results
        """
        result = {
            'success': False,
            'error_message': None,
            'welcome_message': None,
            'current_url': None,
            'timestamp': None
        }
        
        try:
            self.login(username, password)
            
            # Wait for login completion
            login_complete = self.wait_for_login_complete()
            
            if login_complete:
                if self.is_login_successful():
                    result['success'] = True
                    result['welcome_message'] = self.get_welcome_message()
                    log.info("Login successful")
                else:
                    result['error_message'] = self.get_error_message()
                    log.warning(f"Login failed: {result['error_message']}")
            
            result['current_url'] = self.get_url()
            
        except Exception as e:
            result['error_message'] = str(e)
            log.error(f"Login exception: {e}")
        
        return result

    def is_login_successful(self) -> bool:
        """Check if login was successful."""
        try:
            # Check for welcome message in left panel (contains user's first and last name)
            welcome_locator = "#leftPanel p"
            self.wait_helper.wait_for_element(welcome_locator, WaitStrategy.ELEMENT_VISIBLE, timeout=5000)
            welcome_text = self.get_text(welcome_locator)
            return "Welcome" in welcome_text and len(welcome_text) > 10  # Should contain user name
        except:
            return False

    def is_error_message_displayed(self) -> bool:
        """Check if error message is displayed."""
        return self.is_visible(self.ERROR_MESSAGE)

    def get_error_message(self) -> str:
        """Get error message text."""
        try:
            if self.is_visible(self.ERROR_MESSAGE, timeout=3000):
                return self.get_text(self.ERROR_MESSAGE)
            return ""
        except:
            return ""

    def get_welcome_message(self) -> str:
        """Get welcome message after successful login."""
        try:
            welcome_locator = "#leftPanel p"
            if self.is_visible(welcome_locator, timeout=5000):
                return self.get_text(welcome_locator)
            return ""
        except:
            return ""

    def click_forgot_password(self) -> None:
        """Click forgot password link."""
        self.wait_helper.wait_for_and_click(self.FORGOT_PASSWORD_LINK)
        log.info("Clicked forgot password link")

    def click_register(self) -> None:
        """Click register link."""
        self.wait_helper.wait_for_and_click(self.REGISTER_LINK)
        # Wait for page navigation to registration page
        self.page.wait_for_timeout(2000)  # Simple wait for navigation
        log.info("Clicked register link")

    def wait_for_login_complete(self, timeout: int = 10000) -> bool:
        """Wait for login process to complete."""
        try:
            return self.wait_helper.wait_for_custom_condition(
                condition=lambda: (
                    self.is_visible(self.WELCOME_MESSAGE, timeout=1000) or 
                    self.is_visible(self.ERROR_MESSAGE, timeout=1000)
                ),
                timeout=timeout,
                message="Login completion timeout"
            )
        except:
            return False

    def assert_login_page_loaded(self) -> None:
        """Assert that login page is properly loaded."""
        self.assert_helper.assert_element_visible(self.USERNAME_FIELD)
        self.assert_helper.assert_element_visible(self.PASSWORD_FIELD)
        self.assert_helper.assert_element_visible(self.LOGIN_BUTTON)
        self.assert_helper.assert_element_is_clickable(self.LOGIN_BUTTON)
        log.info("Login page loaded successfully")

    def assert_login_failed(self, expected_error_message: Optional[str] = None) -> None:
        """Assert that login failed with expected error."""
        self.assert_helper.assert_element_visible(self.ERROR_MESSAGE)
        
        if expected_error_message:
            self.assert_helper.assert_element_contains_text(self.ERROR_MESSAGE, expected_error_message)
        
        log.info("Login failure assertion verified")

    def assert_login_successful(self) -> None:
        """Assert that login was successful."""
        self.assert_helper.assert_element_visible(self.WELCOME_MESSAGE)
        welcome_text = self.get_text(self.WELCOME_MESSAGE)
        assert "Welcome" in welcome_text, "Welcome message not found"
        log.info("Login success assertion verified")

    def validate_login_form_accessibility(self) -> Dict[str, bool]:
        """Validate basic accessibility of login form."""
        accessibility_results = {
            'username_has_label': False,
            'password_has_label': False,
            'login_button_has_text': False,
            'form_is_keyboard_accessible': False
        }
        
        try:
            username_field = self.page.locator(self.USERNAME_FIELD)
            password_field = self.page.locator(self.PASSWORD_FIELD)
            login_button = self.page.locator(self.LOGIN_BUTTON)
            
            accessibility_results['username_has_label'] = bool(
                username_field.get_attribute('aria-label') or 
                username_field.get_attribute('placeholder') or
                self.page.locator("#loginPanel form p:has-text('Username')").count() > 0
            )
            
            accessibility_results['username_has_placeholder'] = bool(
                username_field.get_attribute('placeholder')
            )
            
            accessibility_results['password_has_label'] = bool(
                password_field.get_attribute('aria-label') or 
                password_field.get_attribute('placeholder') or
                self.page.locator("#loginPanel form p:has-text('Password')").count() > 0
            )
            
            accessibility_results['password_has_placeholder'] = bool(
                password_field.get_attribute('placeholder')
            )
            
            accessibility_results['login_button_has_text'] = bool(
                login_button.get_attribute('value') or
                login_button.text_content()
            )
            
            username_field.focus()
            accessibility_results['form_is_keyboard_accessible'] = (
                username_field.is_visible() or
                password_field.is_visible() or
                login_button.is_visible()
            )
            
        except Exception as e:
            log.error(f"Accessibility validation failed: {e}")
        
        return accessibility_results

    def clear_login_form(self) -> None:
        """Clear all login form fields."""
        self.fill(self.USERNAME_FIELD, "")
        self.fill(self.PASSWORD_FIELD, "")
        log.info("Cleared login form")

    def is_password_field_masked(self) -> bool:
        """Check if password field is properly masked."""
        input_type = self.get_attribute(self.PASSWORD_FIELD, "type")
        return input_type == "password"

    def press_enter_in_password_field(self) -> None:
        """Press Enter key in password field."""
        self.press_key(self.PASSWORD_FIELD, "Enter")
        log.info("Pressed Enter in password field")

    def get_form_validation_state(self) -> Dict[str, Any]:
        """Get current form validation state."""
        return {
            'username_empty': not bool(self.get_text(self.USERNAME_FIELD)),
            'password_empty': not bool(self.get_text(self.PASSWORD_FIELD)),
            'login_enabled': self.is_enabled(self.LOGIN_BUTTON),
            'form_visible': self.is_visible(self.LOGIN_FORM)
        }
