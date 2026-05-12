"""Comprehensive UI test suite for ParaBank Login page."""
import pytest
import random
import string
from datetime import datetime
from playwright.sync_api import Page
from src.pages.login_page import LoginPage
from src.pages.registration_page import RegistrationPage
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.utils.test_data_utils import TestDataUtils
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.login
class TestLoginPage:
    """Enterprise-grade test suite for login functionality."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test environment."""
        self.page = page
        self.login_page = LoginPage(page)
        self.registration_page = RegistrationPage(page)
        self.accounts_page = AccountsOverviewPage(page)
        self.test_data = TestDataUtils()

    @pytest.mark.smoke
    def test_login_page_loads_correctly(self):
        """Test that login page loads with all required elements."""
        self.login_page.navigate_to_login()
        self.login_page.assert_login_page_loaded()
        
        # Verify page title
        assert "ParaBank" in self.page.title()
        assert "Welcome" in self.page.title()

    @pytest.mark.smoke
    def test_login_page_title(self):
        """Test login page title."""
        self.login_page.navigate_to_login()
        assert "ParaBank" in self.page.title()
        assert "Welcome" in self.page.title()

    @pytest.mark.smoke
    def test_login_with_valid_credentials(self):
        """Test login with valid credentials."""
        # Use test data from configuration
        test_user = self.test_data.get_test_user("john")
        
        # Perform login using page object method
        self.login_page.navigate_to_login()
        login_result = self.login_page.login_with_validation(
            test_user["username"], 
            test_user["password"]
        )
        
        # Verify successful login
        assert login_result['success'], "Login should be successful"
        assert login_result['welcome_message'], "Should have welcome message"
        
        # Verify navigation to accounts overview
        self.accounts_page.assert_accounts_overview_loaded()

    @pytest.mark.regression
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials."""
        self.login_page.navigate_to_login()
        
        # Perform login with invalid credentials
        login_result = self.login_page.login_with_validation("invaliduser", "wrongpass")
        
        # Verify login failed
        assert not login_result['success'], "Login should fail with invalid credentials"
        assert login_result['error_message'], "Should display error message"
        
        # Verify still on login page
        self.login_page.assert_login_page_loaded()
        self.login_page.assert_login_failed()


    @pytest.mark.regression
    def test_login_with_empty_credentials(self):
        """Test login fails with empty credentials."""
        self.login_page.navigate_to_login()
        
        # Try to login with empty credentials
        self.login_page.login("", "")
        
        # Verify login failed
        assert not self.login_page.is_login_successful()
        assert self.login_page.is_error_message_displayed()
        
        # Verify error message
        error_msg = self.login_page.get_error_message()
        assert len(error_msg) > 0, "Should display error message for empty credentials"

    @pytest.mark.regression
    def test_login_with_empty_username(self):
        """Test login fails with empty username."""
        self.login_page.navigate_to_login()
        
        # Try to login with empty username
        self.login_page.login("", "password")
        
        # Verify login failed
        assert not self.login_page.is_login_successful()
        assert self.login_page.is_error_message_displayed()

    @pytest.mark.regression
    def test_login_with_empty_password(self):
        """Test login fails with empty password."""
        self.login_page.navigate_to_login()
        
        # Try to login with empty password
        self.login_page.login("username", "")
        
        # Verify login failed
        assert not self.login_page.is_login_successful()
        assert self.login_page.is_error_message_displayed()

    @pytest.mark.usability
    def test_login_form_validation(self):
        """Test login form validation and state."""
        self.login_page.navigate_to_login()
        
        # Check initial form state
        form_state = self.login_page.get_form_validation_state()
        assert form_state['username_empty'], "Username should be empty initially"
        assert form_state['password_empty'], "Password should be empty initially"
        assert form_state['login_enabled'], "Login button should be enabled"
        assert form_state['form_visible'], "Form should be visible"

    @pytest.mark.security
    def test_password_field_is_masked(self):
        """Test that password field is properly masked."""
        self.login_page.navigate_to_login()
        
        # Check password field type
        assert self.login_page.is_password_field_masked(), "Password field should be masked"

    @pytest.mark.accessibility
    def test_login_form_accessibility(self):
        """Test login form accessibility features."""
        self.login_page.navigate_to_login()
        
        # Check accessibility
        accessibility_results = self.login_page.validate_login_form_accessibility()
        
        # Verify basic accessibility features
        # Note: ParaBank login form may not have explicit labels, but has placeholders
        assert accessibility_results['username_has_label'] or accessibility_results['username_has_placeholder'], "Username field should have label or placeholder"
        assert accessibility_results['password_has_label'] or accessibility_results['password_has_placeholder'], "Password field should have label or placeholder"
        assert accessibility_results['login_button_has_text'], "Login button should have text"
        assert accessibility_results['form_is_keyboard_accessible'], "Form should be keyboard accessible"

    @pytest.mark.navigation
    def test_forgot_password_link_navigation(self):
        """Test forgot password link navigation."""
        self.login_page.navigate_to_login()
        
        # Click forgot password link
        self.login_page.click_forgot_password()
        
        # Should navigate to forgot password page
        # Verify URL change or page content
        current_url = self.login_page.get_url()
        assert "lookup" in current_url.lower(), "Should navigate to forgot password page"

    @pytest.mark.regression
    def test_register_link_navigation(self):
        """Test register link navigation."""
        self.login_page.navigate_to_login()
        
        # Click register link
        self.login_page.click_register()
        
        # Verify navigation to registration page
        self.registration_page.assert_registration_page_loaded()

    @pytest.mark.usability
    def test_login_with_enter_key(self):
        """Test login functionality with Enter key."""
        self.login_page.navigate_to_login()
        
        # Fill credentials
        test_user = self.test_data.get_test_user("john")
        self.login_page.enter_username(test_user["username"])
        self.login_page.enter_password(test_user["password"])
        
        # Press Enter in password field
        self.login_page.press_enter_in_password_field()
        
        # Wait for login to process
        login_complete = self.login_page.wait_for_login_complete()
        assert login_complete, "Login should complete with Enter key"
        
        # Verify successful login
        assert self.login_page.is_login_successful(), "Login should be successful with Enter key"

    @pytest.mark.performance
    def test_login_page_load_performance(self):
        """Test login page load performance."""
        start_time = datetime.now()
        self.login_page.navigate_to_login()
        self.login_page.assert_login_page_loaded()
        load_time = (datetime.now() - start_time).total_seconds()
        
        # Page should load within reasonable time (5 seconds)
        assert load_time < 5.0, f"Page load time {load_time}s exceeds threshold"

    @pytest.mark.performance
    def test_login_response_time(self):
        """Test login response time."""
        self.login_page.navigate_to_login()
        
        test_user = self.test_data.get_test_user("john")
        
        start_time = datetime.now()
        login_result = self.login_page.login_with_validation(
            test_user["username"], 
            test_user["password"]
        )
        response_time = (datetime.now() - start_time).total_seconds()
        
        # Login should complete within reasonable time (10 seconds)
        assert response_time < 10.0, f"Login response time {response_time}s exceeds threshold"
        assert login_result['success'], "Login should be successful"

    @pytest.mark.edge_case
    def test_login_with_special_characters(self):
        """Test login with special characters in credentials."""
        self.login_page.navigate_to_login()
        
        # Try login with special characters
        login_result = self.login_page.login_with_validation("user@test.com", "pass@word#123")
        
        # Should handle gracefully (likely fail but not crash)
        assert isinstance(login_result, dict), "Should return result dictionary"
        assert 'success' in login_result, "Should have success status"

    @pytest.mark.edge_case
    def test_login_with_very_long_credentials(self):
        """Test login with very long credentials."""
        self.login_page.navigate_to_login()
        
        # Generate very long credentials
        long_username = 'a' * 100
        long_password = 'b' * 100
        
        # Try login with long credentials
        login_result = self.login_page.login_with_validation(long_username, long_password)
        
        # Should handle gracefully
        assert isinstance(login_result, dict), "Should return result dictionary"
        assert not login_result['success'], "Long credentials should not be accepted"

    @pytest.mark.regression
    def test_clear_login_form(self):
        """Test clearing login form functionality."""
        self.login_page.navigate_to_login()
        
        # Fill form with data
        self.login_page.enter_username("testuser")
        self.login_page.enter_password("testpass")
        
        # Clear form
        self.login_page.clear_login_form()
        
        # Verify form is cleared
        form_state = self.login_page.get_form_validation_state()
        assert form_state['username_empty'], "Username should be empty after clearing"
        assert form_state['password_empty'], "Password should be empty after clearing"

    @pytest.mark.error_handling
    def test_login_error_message_content(self):
        """Test login error message content and display."""
        self.login_page.navigate_to_login()
        
        # Try login with invalid credentials
        login_result = self.login_page.login_with_validation("invalid", "credentials")
        
        # Check error message
        assert not login_result['success'], "Login should fail"
        assert login_result['error_message'], "Should have error message"
        assert len(login_result['error_message']) > 0, "Error message should not be empty"

    @pytest.mark.browser_compatibility
    def test_login_form_javascript_functionality(self):
        """Test login form JavaScript functionality."""
        self.login_page.navigate_to_login()
        
        # Test JavaScript evaluation on form
        form_exists = self.page.evaluate("""
            () => {
                const form = document.querySelector('#loginPanel form');
                return form !== null;
            }
        """)
        
        assert form_exists, "Login form should be accessible via JavaScript"
        
        # Test form filling via JavaScript
        test_user = self.test_data.get_test_user("john")
        self.page.evaluate(f"""
            () => {{
                document.querySelector('.login input[name="username"]').value = '{test_user["username"]}';
                document.querySelector('.login input[name="password"]').value = '{test_user["password"]}';
            }}
        """)
        
        # Submit and verify
        self.login_page.click_login()
        login_complete = self.login_page.wait_for_login_complete()
        assert login_complete, "JavaScript-filled form should submit successfully"

    @pytest.mark.localization
    def test_login_page_localization_elements(self):
        """Test login page localization elements."""
        self.login_page.navigate_to_login()
        
        # Check for proper labels and text
        page_content = self.page.content()
        assert len(page_content) > 0, "Page should have content"
        
        # Check for common login page elements
        assert "username" in page_content.lower() or "user" in page_content.lower(), "Should have username field"
        assert "password" in page_content.lower(), "Should have password field"

    @pytest.mark.responsive
    def test_login_form_responsive_design(self):
        """Test login form responsive design."""
        self.login_page.navigate_to_login()
        
        # Test different viewport sizes
        viewport_sizes = [
            {'width': 1920, 'height': 1080},  # Desktop
            {'width': 768, 'height': 1024},   # Tablet
            {'width': 375, 'height': 667}     # Mobile
        ]
        
        for viewport in viewport_sizes:
            self.page.set_viewport_size(viewport)
            
            # Check if form elements are still visible and functional
            assert self.page.is_visible(self.login_page.USERNAME_FIELD), f"Username field should be visible on {viewport['width']}x{viewport['height']}"
            assert self.page.is_visible(self.login_page.PASSWORD_FIELD), f"Password field should be visible on {viewport['width']}x{viewport['height']}"
            assert self.page.is_visible(self.login_page.LOGIN_BUTTON), f"Login button should be visible on {viewport['width']}x{viewport['height']}"

    @pytest.mark.security
    def test_login_data_privacy(self):
        """Test login data privacy and security."""
        self.login_page.navigate_to_login()
        
        # Check that sensitive data is not exposed inappropriately
        page_content = self.page.content()
        
        # Should not expose passwords in page source
        assert "password" not in page_content.lower() or page_content.count("password") <= 2, "Password data should not be exposed"
        
        # Check that form uses appropriate method
        form_method = self.page.get_attribute("#loginPanel form", "method")
        assert form_method.lower() == "post", "Login form should use POST method"

    @pytest.mark.integration
    def test_complete_login_logout_workflow(self):
        """Test complete login and logout workflow."""
        # Login
        test_user = self.test_data.get_test_user("john")
        self.login_page.navigate_to_login()
        login_result = self.login_page.login_with_validation(
            test_user["username"], 
            test_user["password"]
        )
        assert login_result['success'], "Login should be successful"
        
        # Verify logged in state
        self.accounts_page.assert_accounts_overview_loaded()
        
        # Logout
        self.accounts_page.click_logout()
        
        # Verify logged out state
        self.login_page.assert_login_page_loaded()


@pytest.mark.regression
@pytest.mark.ui
class TestHomePage:
    """Test cases for home page functionality."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test environment."""
        self.page = page
        self.login_page = LoginPage(page)
        self.accounts_page = AccountsOverviewPage(page)
        self.test_data = TestDataUtils()

    @pytest.mark.smoke
    def test_home_page_loads_after_login(self):
        """Test home page loads successfully after login."""
        # Login first
        test_user = self.test_data.get_test_user("john")
        self.login_page.navigate_to_login()
        login_result = self.login_page.login_with_validation(
            test_user["username"], 
            test_user["password"]
        )
        assert login_result['success'], "Login should be successful"
        
        # Verify home/accounts page loads
        self.accounts_page.assert_accounts_overview_loaded()
        assert self.accounts_page.is_accounts_table_visible(), "Accounts table should be visible"
        assert len(self.accounts_page.get_welcome_message()) > 0, "Welcome message should be displayed"

    @pytest.mark.smoke
    def test_navigation_menu_visible(self):
        """Test navigation menu is visible after login."""
        # Login first
        test_user = self.test_data.get_test_user("john")
        self.login_page.navigate_to_login()
        login_result = self.login_page.login_with_validation(
            test_user["username"], 
            test_user["password"]
        )
        assert login_result['success'], "Login should be successful"
        
        # Check navigation menu
        nav_menu_selector = ".leftmenu"
        assert self.page.is_visible(nav_menu_selector), "Navigation menu should be visible"
        
        # Check for key navigation links
        navigation_links = [
            "a[href*='overview.htm']",  # Accounts Overview
            "a[href*='transfer.htm']",   # Transfer Funds
            "a[href*='billpay.htm']",    # Bill Pay
            "a[href*='findtrans.htm']",  # Find Transactions
            "a[href*='requestloan.htm']", # Request Loan
            "a[href*='openaccount.htm']", # Open New Account
            "a[href*='logout.htm']",     # Logout
        ]
        
        for link_selector in navigation_links:
            link_exists = self.page.locator(link_selector).count() > 0
            log.info(f"Navigation link {link_selector}: {'Found' if link_exists else 'Not found'}")
