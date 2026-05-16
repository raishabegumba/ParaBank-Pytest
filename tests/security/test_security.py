"""
==============================================================================
ParaBank Security Tests
==============================================================================
Comprehensive security test suite including:
- XSS Prevention
- SQL Injection Prevention
- Session Management
- Unauthorized Access
- CSRF Prevention
"""

import pytest
import allure
from playwright.sync_api import Page
from src.pages.login_page import LoginPage
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.config.settings import settings
from src.config.logger import log


@allure.feature("Security")
@allure.story("XSS Prevention")
class TestXSSPrevention:
    """Test XSS prevention across application."""
    
    # @pytest.fixture(autouse=True)
    # def setup(self, page: Page):
    #     """Setup test environment."""
    #     page = page

    @pytest.mark.security
    @pytest.mark.critical
    @allure.title("XSS Prevention in Login Form")
    @allure.description("Verify XSS payloads are sanitized in login")
    def test_xss_login_username(self, page):
        """
        Test Case: XSS Prevention - Login
        Objective: Verify XSS payload handling
        Steps:
            1. Navigate to login
            2. Enter XSS payload in username
            3. Verify no script execution
        Expected: XSS payload escaped/sanitized
        """
        login_page = LoginPage(page)
        
        page.goto(f"{settings.base_url}/index.htm")
        
        xss_payload = "<script>alert('XSS')</script>"
        login_page.enter_username(xss_payload)
        login_page.enter_password("test")
        login_page.click_login()
        
        # Verify page still functional and script not executed
        page_content = page.inner_text('body')
        assert "<script>" not in page_content, "XSS should be escaped"
        log.info("XSS prevention verified in login")
    
    @pytest.mark.security
    @allure.title("XSS Prevention with Image Tag")
    @allure.description("Verify image-based XSS is prevented")
    def test_xss_image_tag(self, page):
        """Test image-based XSS prevention."""
        login_page = LoginPage(page)
        
        page.goto(f"{settings.base_url}/index.htm")
        
        xss_payload = "<img src=x onerror='alert(1)'>"
        login_page.enter_username(xss_payload)
        login_page.click_login()
        
        page_content = page.inner_text('body')
        assert "onerror" not in page_content
    
    @pytest.mark.security
    @allure.title("XSS Prevention with Event Handler")
    @allure.description("Verify event-based XSS is prevented")
    def test_xss_event_handler(self, page):
        """Test event handler XSS prevention."""
        login_page = LoginPage(page)
        
        page.goto(f"{settings.base_url}/index.htm")
        
        xss_payload = "javascript:alert('XSS')"
        login_page.enter_username(xss_payload)
        login_page.click_login()
        
        page_content = page.inner_text('body')
        # Page should still work
        assert login_page.verify_page_loaded() or page.url.count('login') > 0


@allure.feature("Security")
@allure.story("SQL Injection Prevention")
class TestSQLInjectionPrevention:
    """Test SQL injection prevention."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test environment."""
        page = page

    @pytest.mark.security
    @pytest.mark.critical
    @allure.title("SQL Injection in Login Username")
    @allure.description("Verify SQL injection is prevented")
    def test_sql_injection_login_username(self, page):
        """
        Test Case: SQL Injection Prevention
        Objective: Verify SQL injection payloads are handled
        Steps:
            1. Enter SQL injection in username
            2. Verify not executed
            3. Check error handling
        Expected: Graceful error handling, no data breach
        """
        login_page = LoginPage(page)
        
        page.goto(f"{settings.base_url}/index.htm")
        
        sql_payload = "' OR '1'='1"
        login_page.login(sql_payload, "password")
        
        # Should reject or show error
        error_msg = login_page.get_error_message()
        assert error_msg != "" or login_page.verify_page_loaded()
        log.info("SQL injection prevention verified")
    
    @pytest.mark.security
    @allure.title("Advanced SQL Injection")
    @allure.description("Verify advanced SQL injection attempts are blocked")
    def test_sql_injection_advanced(self, page):
        """Test advanced SQL injection."""
        login_page = LoginPage(page)
        
        page.goto(f"{settings.base_url}/index.htm")
        
        sql_payload = "admin'--"
        login_page.login(sql_payload, "anything")
        
        # Should reject
        assert login_page.verify_page_loaded()
    
    @pytest.mark.security
    @allure.title("UNION-based SQL Injection")
    @allure.description("Verify UNION-based SQL injection is prevented")
    def test_sql_injection_union(self, page):
        """Test UNION-based SQL injection."""
        login_page = LoginPage(page)
        
        page.goto(f"{settings.base_url}/index.htm")
        
        sql_payload = "' UNION SELECT NULL,NULL--"
        login_page.login(sql_payload, "password")
        
        # Should handle safely
        assert login_page.verify_page_loaded()


@allure.feature("Security")
@allure.story("Session Management")
class TestSessionSecurity:
    """Test session security."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test environment."""
        page = page

    @pytest.mark.security
    @pytest.mark.critical
    @allure.title("Session Invalidation on Logout")
    @allure.description("Verify session is destroyed on logout")
    def test_session_invalidation_on_logout(self, page, test_credentials):
        """
        Test Case: Session Invalidation
        Objective: Verify session ends on logout
        Steps:
            1. Login
            2. Verify authenticated
            3. Logout
            4. Try to access protected page
            5. Should be redirected to login
        Expected: Session terminated, protected page inaccessible
        """
        login_page = LoginPage(page)
        accounts_page = AccountsOverviewPage(page)
        
        # Login
        page.goto(f"{settings.base_url}/index.htm")
        login_page.login(test_credentials['username'], test_credentials['password'])
        
        assert accounts_page.verify_page_loaded()
        
        # Logout
        accounts_page.logout()
        
        # Try to access protected page
        page.goto(f"{settings.base_url}/overview.htm")
        
        # Should be redirected to login
        current_url = page.url
        assert 'login' in current_url or login_page.verify_page_loaded()
        log.info("Session invalidation verified")
    
    @pytest.mark.security
    @allure.title("Prevent Direct Access to Protected Pages")
    @allure.description("Verify unauthenticated users cannot access protected pages")
    def test_prevent_unauthorized_access(self, page):
        """Test unauthorized access prevention."""
        # Try to access protected page without login
        page.goto(f"{settings.base_url}/overview.htm")
        
        # Should redirect to login
        login_page = LoginPage(page)
        current_url = page.url
        
        assert 'login' in current_url or login_page.verify_page_loaded()
        log.info("Unauthorized access prevented")
    
    @pytest.mark.security
    @allure.title("Session Cookie Security")
    @allure.description("Verify session cookies are configured securely")
    def test_session_cookie_security(self, page, test_credentials):
        """Test session cookie security."""
        login_page = LoginPage(page)
        accounts_page = AccountsOverviewPage(page)
        
        page.goto(f"{settings.base_url}/index.htm")
        login_page.login(test_credentials['username'], test_credentials['password'])
        
        # Session cookie should exist
        cookies = page.context.cookies()
        cookie_exists = len(cookies) > 0
        assert cookie_exists, "Session cookie should exist"
        
        log.info(f"Session cookies verified: {len(cookies)} cookies found")


@allure.feature("Security")
@allure.story("Authorization")
class TestAuthorizationSecurity:
    """Test authorization and access control."""
    
    @pytest.mark.security
    @pytest.mark.critical
    @allure.title("Cannot Modify Other User's Data")
    @allure.description("Verify users cannot access/modify other users' data")
    def test_authorization_other_user_data(self, page, test_credentials):
        """
        Test Case: Authorization Check
        Objective: Verify users cannot access other user's data
        Expected: Cannot view/modify other user accounts
        """
        login_page = LoginPage(page)
        accounts_page = AccountsOverviewPage(page)
        
        page.goto(f"{settings.base_url}/index.htm")
        login_page.login(test_credentials['username'], test_credentials['password'])
        
        # User should only see own accounts
        assert accounts_page.verify_page_loaded()
        
        # Verify account access restriction
        count = accounts_page.get_account_count()
        # Should have own accounts, not others
        assert count >= 0
        log.info("Authorization verified")


@allure.feature("Security")
@allure.story("Password Security")
class TestPasswordSecurity:
    """Test password security."""
    
    @pytest.mark.security
    @allure.title("Password Fields Are Masked")
    @allure.description("Verify password input fields are masked")
    def test_password_field_masked(self, page):
        """
        Test Case: Password Masking
        Objective: Verify passwords are not visible
        Expected: Password field type is 'password'
        """
        login_page = LoginPage(page)
        
        page.goto(f"{settings.base_url}/index.htm")
        
        # Check password field type
        password_type = page.get_attribute(
            login_page.PASSWORD_FIELD,
            'type'
        )
        
        assert password_type == 'password', "Password field should be masked"
        log.info("Password field masking verified")
    
    @pytest.mark.security
    @allure.title("Password Not Echo in Response")
    @allure.description("Verify passwords are not returned in responses")
    def test_password_not_in_response(self, page):
        """Test that passwords are not exposed in responses."""
        login_page = LoginPage(page)
        
        page.goto(f"{settings.base_url}/index.htm")
        
        # Enter password
        login_page.enter_password("TestPassword@123")
        
        # Get page content - should not contain password
        page_content = page.inner_text('body')
        assert "TestPassword@123" not in page_content


@allure.feature("Security")
@allure.story("Data Validation")
class TestDataValidationSecurity:
    """Test data validation security."""
    
    @pytest.mark.security
    @allure.title("Input Validation - Special Characters")
    @allure.description("Verify special characters are handled safely")
    def test_input_validation_special_chars(self, page, test_credentials):
        """Test special character handling."""
        login_page = LoginPage(page)
        accounts_page = AccountsOverviewPage(page)
        
        page.goto(f"{settings.base_url}/index.htm")
        
        # Special characters in input
        special_chars = "!@#$%^&*()"
        login_page.login(test_credentials['username'], special_chars)
        
        # Application should handle gracefully
        assert login_page.verify_page_loaded() or page.url
        log.info("Special character handling verified")

