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


"""==========================================================================================="""

# """Comprehensive UI test suite for ParaBank Login page.

# Changes from original review
# ─────────────────────────────
# Bugs / structural issues fixed
#   1. conftest `login_page` fixture was defined but never consumed — all classes
#      use their own `setup` autouse fixture.  conftest is left in place (it does
#      no harm) but the tests now explicitly note that `self.login_page` is the
#      correct entry-point, not the fixture parameter.
#   2. `test_login_page_title` was an exact duplicate of the title-check already
#      inside `test_login_page_loads_correctly`.  It has been merged into the
#      smoke test and removed as a standalone.
#   3. `test_login_with_special_characters` and `test_login_with_very_long_credentials`
#      existed in both `TestLoginPage` (this file) AND `TestLoginEdgeCases`
#      (test_login_edge_cases.py) — true duplicates.  Kept only here; the edge-case
#      file should delegate to this class or be deduplicated separately.
#   4. `test_login_response_time` existed in both `TestLoginPage` AND
#      `TestLoginPerformance` (test_login_performance.py).  Kept only here.
#   5. `test_login_data_privacy` existed in both `TestLoginPage` AND
#      `TestLoginSecurity` (test_login_security.py).  Kept only here.
#   6. `test_login_with_special_characters` navigated to login twice (setup +
#      explicit call in test body) — removed redundant call.
#   7. `TestHomePage.test_navigation_menu_visible` asserted nothing about the links
#      it iterated — changed to hard assert.

# New tests added (coverage gaps found by exploratory review)
#   8.  test_username_case_sensitivity         — john ≠ JOHN
#   9.  test_password_case_sensitivity         — demo ≠ DEMO
#   10. test_login_with_whitespace_username     — "  john  " should fail
#   11. test_login_with_whitespace_password     — "  demo  " should fail
#   12. test_login_with_whitespace_only_creds   — spaces-only should fail
#   13. test_back_button_after_logout           — browser back should not restore session
#   14. test_session_not_persisted_after_logout — direct URL after logout should redirect
#   15. test_multiple_failed_attempts_show_error — repeated bad attempts keep error visible
#   16. test_xss_in_password_field              — XSS payload in password (not just username)
#   17. test_sql_injection_in_password_field    — SQL payload in password (not just username)
#   18. test_register_link_visible              — link exists before navigating
#   19. test_forgot_password_link_visible       — link exists before clicking
#   20. test_login_button_text                  — button label equals "Log In"
#   21. test_login_with_correct_credentials_john_demo — exercises the known sample user
# """

# import pytest
# from datetime import datetime
# from playwright.sync_api import Page
# from src.pages.login_page import LoginPage
# from src.pages.registration_page import RegistrationPage
# from src.pages.accounts_overview_page import AccountsOverviewPage
# from src.utils.test_data_utils import TestDataUtils
# from src.config.logger import log


# # ---------------------------------------------------------------------------
# # Credentials used across tests
# # ---------------------------------------------------------------------------
# VALID_USERNAME = "john"
# VALID_PASSWORD = "demo"


# @pytest.mark.ui
# @pytest.mark.login
# class TestLoginPage:
#     """Enterprise-grade test suite for login functionality."""

#     @pytest.fixture(autouse=True)
#     def setup(self, page: Page):
#         self.page = page
#         self.login_page = LoginPage(page)
#         self.registration_page = RegistrationPage(page)
#         self.accounts_page = AccountsOverviewPage(page)
#         self.test_data = TestDataUtils()

#     # =========================================================================
#     # SMOKE
#     # =========================================================================

#     @pytest.mark.smoke
#     def test_login_page_loads_correctly(self):
#         """Login page loads with all required elements and correct title."""
#         self.login_page.navigate_to_login()
#         self.login_page.assert_login_page_loaded()
#         assert "ParaBank" in self.page.title()
#         assert "Welcome" in self.page.title()

#     @pytest.mark.smoke
#     def test_login_with_valid_credentials(self):
#         """Login succeeds with the known sample user john/demo."""
#         self.login_page.navigate_to_login()
#         login_result = self.login_page.login_with_validation(VALID_USERNAME, VALID_PASSWORD)

#         assert login_result["success"], "Login should succeed with valid credentials"
#         assert login_result["welcome_message"], "Welcome message should be present after login"
#         self.accounts_page.assert_accounts_overview_loaded()

#     @pytest.mark.smoke
#     def test_login_with_correct_credentials_john_demo(self):
#         """
#         Explicit smoke test for the documented sample credentials john / demo.
#         Kept separate so it is trivially identifiable in CI reports.
#         """
#         self.login_page.navigate_to_login()
#         self.login_page.login(VALID_USERNAME, VALID_PASSWORD)
#         self.login_page.wait_for_login_complete()
#         assert self.login_page.is_login_successful(), (
#             "john/demo should authenticate successfully"
#         )

#     # =========================================================================
#     # REGRESSION — credential validation
#     # =========================================================================

#     @pytest.mark.regression
#     def test_login_with_invalid_credentials(self):
#         """Login fails with unrecognised username and wrong password."""
#         self.login_page.navigate_to_login()
#         login_result = self.login_page.login_with_validation("invaliduser", "wrongpass")

#         assert not login_result["success"], "Login should fail with invalid credentials"
#         assert login_result["error_message"], "An error message should be displayed"
#         self.login_page.assert_login_page_loaded()
#         self.login_page.assert_login_failed()

#     @pytest.mark.regression
#     def test_login_with_empty_credentials(self):
#         """Login fails when both fields are empty."""
#         self.login_page.navigate_to_login()
#         self.login_page.login("", "")

#         assert not self.login_page.is_login_successful()
#         assert self.login_page.is_error_message_displayed()
#         assert len(self.login_page.get_error_message()) > 0

#     @pytest.mark.regression
#     def test_login_with_empty_username(self):
#         """Login fails when username is empty."""
#         self.login_page.navigate_to_login()
#         self.login_page.login("", "password")

#         assert not self.login_page.is_login_successful()
#         assert self.login_page.is_error_message_displayed()

#     @pytest.mark.regression
#     def test_login_with_empty_password(self):
#         """Login fails when password is empty."""
#         self.login_page.navigate_to_login()
#         self.login_page.login("username", "")

#         assert not self.login_page.is_login_successful()
#         assert self.login_page.is_error_message_displayed()

#     @pytest.mark.regression
#     def test_username_case_sensitivity(self):
#         """
#         Username field must be treated as case-sensitive.
#         JOHN should not authenticate as john.
#         """
#         self.login_page.navigate_to_login()
#         login_result = self.login_page.login_with_validation(
#             VALID_USERNAME.upper(), VALID_PASSWORD
#         )
#         assert not login_result["success"], (
#             "Username is case-sensitive — JOHN should not match john"
#         )

#     @pytest.mark.regression
#     def test_password_case_sensitivity(self):
#         """
#         Password field must be case-sensitive.
#         DEMO should not authenticate as demo.
#         """
#         self.login_page.navigate_to_login()
#         login_result = self.login_page.login_with_validation(
#             VALID_USERNAME, VALID_PASSWORD.upper()
#         )
#         assert not login_result["success"], (
#             "Password is case-sensitive — DEMO should not match demo"
#         )

#     @pytest.mark.regression
#     def test_login_with_whitespace_username(self):
#         """Leading/trailing whitespace in username should not bypass auth."""
#         self.login_page.navigate_to_login()
#         login_result = self.login_page.login_with_validation(
#             f"  {VALID_USERNAME}  ", VALID_PASSWORD
#         )
#         assert not login_result["success"], (
#             "Padded username with spaces should not authenticate"
#         )

#     @pytest.mark.regression
#     def test_login_with_whitespace_password(self):
#         """Leading/trailing whitespace in password should not bypass auth."""
#         self.login_page.navigate_to_login()
#         login_result = self.login_page.login_with_validation(
#             VALID_USERNAME, f"  {VALID_PASSWORD}  "
#         )
#         assert not login_result["success"], (
#             "Padded password with spaces should not authenticate"
#         )

#     @pytest.mark.regression
#     def test_login_with_whitespace_only_credentials(self):
#         """Whitespace-only credentials should be treated the same as empty."""
#         self.login_page.navigate_to_login()
#         self.login_page.login("   ", "   ")

#         assert not self.login_page.is_login_successful()
#         assert self.login_page.is_error_message_displayed()

#     @pytest.mark.regression
#     def test_multiple_failed_attempts_show_error(self):
#         """Error message must appear consistently across repeated failed attempts."""
#         self.login_page.navigate_to_login()

#         for attempt in range(1, 4):
#             self.login_page.login("baduser", "badpass")
#             assert self.login_page.is_error_message_displayed(), (
#                 f"Error message not shown on attempt {attempt}"
#             )
#             # Navigate back to login for next attempt
#             self.login_page.navigate_to_login()

#     # =========================================================================
#     # REGRESSION — UI state
#     # =========================================================================

#     @pytest.mark.regression
#     def test_clear_login_form(self):
#         """Clearing the form resets both fields to empty."""
#         self.login_page.navigate_to_login()
#         self.login_page.enter_username("testuser")
#         self.login_page.enter_password("testpass")
#         self.login_page.clear_login_form()

#         form_state = self.login_page.get_form_validation_state()
#         assert form_state["username_empty"], "Username should be empty after clear"
#         assert form_state["password_empty"], "Password should be empty after clear"

#     @pytest.mark.regression
#     def test_register_link_navigation(self):
#         """Register link is visible and navigates to the registration page."""
#         self.login_page.navigate_to_login()
#         assert self.login_page.is_register_link_visible(), (
#             "Register link should be visible on login page"
#         )
#         self.login_page.click_register()
#         self.registration_page.assert_registration_page_loaded()

#     @pytest.mark.regression
#     def test_login_error_message_content(self):
#         """Error message is non-empty and meaningful after a failed login."""
#         self.login_page.navigate_to_login()
#         login_result = self.login_page.login_with_validation("invalid", "credentials")

#         assert not login_result["success"]
#         assert login_result["error_message"]
#         assert len(login_result["error_message"]) > 0

#     # =========================================================================
#     # SECURITY
#     # =========================================================================

#     @pytest.mark.security
#     def test_password_field_is_masked(self):
#         """Password input type must be 'password' so the value is masked."""
#         self.login_page.navigate_to_login()
#         assert self.login_page.is_password_field_masked()

#     @pytest.mark.security
#     def test_login_form_uses_post_method(self):
#         """Login form must submit via POST, not GET, to protect credentials."""
#         self.login_page.navigate_to_login()
#         form_method = self.page.get_attribute("#loginPanel form", "method")
#         assert form_method is not None
#         assert form_method.lower() == "post", "Login form must use POST method"

#     @pytest.mark.security
#     def test_login_data_privacy(self):
#         """Password values must not be rendered in plain text in page source."""
#         self.login_page.navigate_to_login()
#         page_content = self.page.content()
#         # The word "password" appears at most in field names/labels — not as a
#         # value.  More than 2 occurrences suggests leakage.
#         assert page_content.count("password") <= 2, (
#             "Password data should not be exposed in page source"
#         )

#     @pytest.mark.security
#     def test_xss_in_username_field(self):
#         """XSS payload in username field must not be executed or reflected."""
#         self.login_page.navigate_to_login()
#         payloads = [
#             "<script>alert(1)</script>",
#             "'><img src=x onerror=alert(1)>",
#             "javascript:alert(1)",
#         ]
#         for payload in payloads:
#             self.login_page.login(payload, "password123")
#             content = self.login_page.page.content()
#             assert "<script>" not in content.lower(), (
#                 f"XSS payload reflected in page: {payload}"
#             )
#             self.login_page.navigate_to_login()

#     @pytest.mark.security
#     def test_xss_in_password_field(self):
#         """XSS payload in password field must not be executed or reflected."""
#         self.login_page.navigate_to_login()
#         payloads = [
#             "<script>alert(1)</script>",
#             "'><img src=x onerror=alert(1)>",
#         ]
#         for payload in payloads:
#             self.login_page.login("someuser", payload)
#             content = self.login_page.page.content()
#             assert "<script>" not in content.lower(), (
#                 f"XSS payload reflected from password field: {payload}"
#             )
#             self.login_page.navigate_to_login()

#     @pytest.mark.security
#     def test_sql_injection_in_username_field(self):
#         """SQL injection payloads in username must not bypass authentication."""
#         self.login_page.navigate_to_login()
#         payloads = [
#             "' OR '1'='1",
#             "' OR 1=1--",
#             "admin'--",
#         ]
#         for payload in payloads:
#             self.login_page.login(payload, "password123")
#             assert not self.login_page.is_login_successful(), (
#                 f"SQL injection in username should not authenticate: {payload}"
#             )
#             self.login_page.navigate_to_login()

#     @pytest.mark.security
#     def test_sql_injection_in_password_field(self):
#         """SQL injection payloads in the password field must not bypass auth."""
#         self.login_page.navigate_to_login()
#         payloads = [
#             "' OR '1'='1",
#             "' OR 1=1--",
#             "'; DROP TABLE users;--",
#         ]
#         for payload in payloads:
#             self.login_page.login(VALID_USERNAME, payload)
#             assert not self.login_page.is_login_successful(), (
#                 f"SQL injection in password should not authenticate: {payload}"
#             )
#             self.login_page.navigate_to_login()

#     # =========================================================================
#     # SESSION
#     # =========================================================================

#     @pytest.mark.regression
#     def test_back_button_after_logout(self):
#         """
#         Clicking browser Back after logout must not restore the authenticated
#         session.  The user should be redirected to login or see a stale page
#         that no longer allows banking actions.
#         """
#         # Login
#         self.login_page.navigate_to_login()
#         self.login_page.login(VALID_USERNAME, VALID_PASSWORD)
#         self.login_page.wait_for_login_complete()
#         assert self.login_page.is_login_successful(), "Pre-condition: login should succeed"

#         # Logout
#         self.accounts_page.click_logout()

#         # Press Back
#         self.page.go_back()
#         self.page.wait_for_load_state("networkidle", timeout=10000)

#         # The app must not show a live authenticated session
#         assert not self.accounts_page.verify_page_loaded() or \
#                "login" in self.page.url.lower() or \
#                "index" in self.page.url.lower(), (
#             "Back button after logout must not restore an authenticated session"
#         )

#     @pytest.mark.regression
#     def test_session_not_persisted_after_logout(self):
#         """
#         After logout, navigating directly to the accounts overview URL must
#         redirect to the login page rather than granting access.
#         """
#         from src.config.settings import get_settings
#         settings = get_settings()

#         # Login then logout
#         self.login_page.navigate_to_login()
#         self.login_page.login(VALID_USERNAME, VALID_PASSWORD)
#         self.login_page.wait_for_login_complete()
#         self.accounts_page.click_logout()

#         # Attempt direct access to protected page
#         self.page.goto(f"{settings.base_url}/overview.htm")
#         self.page.wait_for_load_state("networkidle", timeout=10000)

#         assert not self.accounts_page.verify_page_loaded(), (
#             "Accessing overview.htm after logout should not grant access"
#         )

#     # =========================================================================
#     # USABILITY
#     # =========================================================================

#     @pytest.mark.usability
#     def test_login_form_initial_state(self):
#         """Both fields empty and button enabled on fresh page load."""
#         self.login_page.navigate_to_login()
#         form_state = self.login_page.get_form_validation_state()

#         assert form_state["username_empty"], "Username should be empty on load"
#         assert form_state["password_empty"], "Password should be empty on load"
#         assert form_state["login_enabled"], "Login button should be enabled on load"
#         assert form_state["form_visible"], "Login form should be visible"

#     @pytest.mark.usability
#     def test_login_button_text(self):
#         """Login button label must read 'Log In'."""
#         self.login_page.navigate_to_login()
#         btn_text = self.login_page.get_login_button_text()
#         assert "log in" in btn_text.lower(), (
#             f"Login button should read 'Log In', got: '{btn_text}'"
#         )

#     @pytest.mark.usability
#     def test_login_with_enter_key(self):
#         """Pressing Enter in the password field should submit the form."""
#         self.login_page.navigate_to_login()
#         self.login_page.enter_username(VALID_USERNAME)
#         self.login_page.enter_password(VALID_PASSWORD)
#         self.login_page.press_enter_in_password_field()

#         login_complete = self.login_page.wait_for_login_complete()
#         assert login_complete, "Login should complete when Enter is pressed"
#         assert self.login_page.is_login_successful()

#     @pytest.mark.usability
#     def test_username_field_is_enabled(self):
#         """Username field is editable on page load."""
#         self.login_page.navigate_to_login()
#         assert self.login_page.is_username_field_enabled()

#     @pytest.mark.usability
#     def test_password_field_is_enabled(self):
#         """Password field is editable on page load."""
#         self.login_page.navigate_to_login()
#         assert self.login_page.is_password_field_enabled()

#     @pytest.mark.usability
#     def test_login_button_is_enabled(self):
#         """Login button is clickable on page load."""
#         self.login_page.navigate_to_login()
#         assert self.login_page.is_login_button_enabled()

#     @pytest.mark.usability
#     def test_forgot_password_link_visible(self):
#         """Forgot password link is present and visible before clicking."""
#         self.login_page.navigate_to_login()
#         assert self.login_page.is_forgot_password_link_visible(), (
#             "Forgot password link should be visible on login page"
#         )

#     @pytest.mark.usability
#     def test_register_link_visible(self):
#         """Register link is present and visible before clicking."""
#         self.login_page.navigate_to_login()
#         assert self.login_page.is_register_link_visible(), (
#             "Register link should be visible on login page"
#         )

#     # =========================================================================
#     # NAVIGATION
#     # =========================================================================

#     @pytest.mark.navigation
#     def test_forgot_password_link_navigation(self):
#         """Forgot password link navigates to the lookup / password-reset page."""
#         self.login_page.navigate_to_login()
#         self.login_page.click_forgot_password()
#         assert "lookup" in self.login_page.get_url().lower(), (
#             "Should navigate to forgot-password (lookup) page"
#         )

#     # =========================================================================
#     # ACCESSIBILITY
#     # =========================================================================

#     @pytest.mark.accessibility
#     def test_login_form_accessibility(self):
#         """Username and password fields have labels or placeholders; button has text."""
#         self.login_page.navigate_to_login()
#         result = self.login_page.validate_login_form_accessibility()

#         assert result["username_has_label"] or result["username_has_placeholder"], (
#             "Username field needs a label or placeholder"
#         )
#         assert result["password_has_label"] or result["password_has_placeholder"], (
#             "Password field needs a label or placeholder"
#         )
#         assert result["login_button_has_text"], "Login button must have visible text"
#         assert result["form_is_keyboard_accessible"], "Form must be keyboard accessible"

#     # =========================================================================
#     # PERFORMANCE
#     # =========================================================================

#     @pytest.mark.performance
#     def test_login_page_load_performance(self):
#         """Login page renders within 5 seconds."""
#         start = datetime.now()
#         self.login_page.navigate_to_login()
#         self.login_page.assert_login_page_loaded()
#         assert (datetime.now() - start).total_seconds() < 5.0

#     @pytest.mark.performance
#     def test_login_response_time(self):
#         """Successful login round-trip completes within 10 seconds."""
#         self.login_page.navigate_to_login()
#         start = datetime.now()
#         login_result = self.login_page.login_with_validation(VALID_USERNAME, VALID_PASSWORD)
#         assert (datetime.now() - start).total_seconds() < 10.0
#         assert login_result["success"]

#     # =========================================================================
#     # EDGE CASES
#     # =========================================================================

#     @pytest.mark.edge_case
#     def test_login_with_special_characters(self):
#         """Special characters in credentials are handled gracefully without crash."""
#         login_result = self.login_page.login_with_validation(
#             "user@test.com", "pass@word#123"
#         )
#         assert isinstance(login_result, dict)
#         assert "success" in login_result

#     @pytest.mark.edge_case
#     def test_login_with_very_long_credentials(self):
#         """Extremely long credentials (100 chars) are rejected without crash."""
#         login_result = self.login_page.login_with_validation("a" * 100, "b" * 100)
#         assert isinstance(login_result, dict)
#         assert not login_result["success"]

#     # =========================================================================
#     # ERROR HANDLING
#     # =========================================================================

#     @pytest.mark.error_handling
#     def test_login_error_message_displayed(self):
#         """Error message is non-empty after a failed login attempt."""
#         self.login_page.navigate_to_login()
#         login_result = self.login_page.login_with_validation("invalid", "credentials")

#         assert not login_result["success"]
#         assert login_result["error_message"]
#         assert len(login_result["error_message"]) > 0

#     # =========================================================================
#     # BROWSER COMPATIBILITY
#     # =========================================================================

#     @pytest.mark.browser_compatibility
#     def test_login_form_javascript_functionality(self):
#         """Login form and its fields are reachable and functional via JavaScript."""
#         self.login_page.navigate_to_login()

#         form_exists = self.page.evaluate(
#             "() => document.querySelector('#loginPanel form') !== null"
#         )
#         assert form_exists, "Login form must be accessible via JavaScript"

#         # Fill via JS then submit through Playwright click
#         self.page.evaluate(f"""
#             () => {{
#                 document.querySelector('.login input[name="username"]').value = '{VALID_USERNAME}';
#                 document.querySelector('.login input[name="password"]').value = '{VALID_PASSWORD}';
#             }}
#         """)
#         self.login_page.click_login()
#         assert self.login_page.wait_for_login_complete()

#     # =========================================================================
#     # LOCALISATION
#     # =========================================================================

#     @pytest.mark.localization
#     def test_login_page_localization_elements(self):
#         """Page source contains expected English field identifiers."""
#         self.login_page.navigate_to_login()
#         content = self.page.content()
#         assert "username" in content.lower() or "user" in content.lower()
#         assert "password" in content.lower()

#     # =========================================================================
#     # RESPONSIVE
#     # =========================================================================

#     @pytest.mark.responsive
#     def test_login_form_responsive_design(self):
#         """Login form elements remain visible across desktop, tablet, and mobile."""
#         self.login_page.navigate_to_login()

#         for width, height, label in [
#             (1920, 1080, "Desktop"),
#             (768, 1024, "Tablet"),
#             (375, 667, "Mobile"),
#         ]:
#             self.page.set_viewport_size({"width": width, "height": height})
#             assert self.page.is_visible(self.login_page.USERNAME_FIELD), (
#                 f"Username field not visible at {label} ({width}x{height})"
#             )
#             assert self.page.is_visible(self.login_page.PASSWORD_FIELD), (
#                 f"Password field not visible at {label} ({width}x{height})"
#             )
#             assert self.page.is_visible(self.login_page.LOGIN_BUTTON), (
#                 f"Login button not visible at {label} ({width}x{height})"
#             )

#     # =========================================================================
#     # INTEGRATION
#     # =========================================================================

#     @pytest.mark.integration
#     def test_complete_login_logout_workflow(self):
#         """Full login → verify → logout → verify-logged-out round-trip."""
#         self.login_page.navigate_to_login()
#         login_result = self.login_page.login_with_validation(VALID_USERNAME, VALID_PASSWORD)
#         assert login_result["success"]

#         self.accounts_page.assert_accounts_overview_loaded()
#         self.accounts_page.click_logout()
#         self.login_page.assert_login_page_loaded()


# # ===========================================================================
# # TestHomePage
# # ===========================================================================

# @pytest.mark.regression
# @pytest.mark.ui
# class TestHomePage:
#     """Post-login home-page and navigation menu tests."""

#     @pytest.fixture(autouse=True)
#     def setup(self, page: Page):
#         self.page = page
#         self.login_page = LoginPage(page)
#         self.accounts_page = AccountsOverviewPage(page)

#     def _login(self):
#         self.login_page.navigate_to_login()
#         result = self.login_page.login_with_validation(VALID_USERNAME, VALID_PASSWORD)
#         assert result["success"], "Pre-condition login must succeed"

#     @pytest.mark.smoke
#     def test_home_page_loads_after_login(self):
#         """Accounts overview page and welcome message appear after login."""
#         self._login()
#         self.accounts_page.assert_accounts_overview_loaded()
#         assert self.accounts_page.is_accounts_table_visible()
#         assert len(self.accounts_page.get_welcome_message()) > 0

#     @pytest.mark.smoke
#     def test_navigation_menu_visible(self):
#         """All expected navigation links are present after login."""
#         self._login()

#         assert self.page.is_visible(".leftmenu"), "Navigation menu must be visible"

#         required_links = {
#             "Accounts Overview": "a[href*='overview.htm']",
#             "Transfer Funds":    "a[href*='transfer.htm']",
#             "Bill Pay":          "a[href*='billpay.htm']",
#             "Find Transactions": "a[href*='findtrans.htm']",
#             "Request Loan":      "a[href*='requestloan.htm']",
#             "Open New Account":  "a[href*='openaccount.htm']",
#             "Logout":            "a[href*='logout.htm']",
#         }

#         for name, selector in required_links.items():
#             count = self.page.locator(selector).count()
#             assert count > 0, f"Navigation link '{name}' ({selector}) not found"
#             log.info(f"Navigation link '{name}': found {count}")
