"""Comprehensive login page tests covering all scenarios."""
import pytest
from playwright.sync_api import Page
from src.pages.login_page import LoginPage
from src.utils.wait_helpers import WaitStrategy
from src.fixtures.test_data_fixtures import user_test_data, security_test_data, boundary_test_data
from src.config.settings import get_settings
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.login
@pytest.mark.smoke
class TestLoginComprehensive:
    """Comprehensive login page test suite."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test instance."""
        self.login_page = LoginPage(page)
        self.login_page.navigate_to_login()
    
    @pytest.mark.positive
    def test_valid_login(self, user_test_data):
        """Test login with valid credentials."""
        # Arrange
        valid_user = user_test_data['valid_user']
        
        # Act
        self.login_page.login(valid_user['username'], valid_user['password'])
        
        # Assert
        self.login_page.assert_login_successful()
        assert self.login_page.is_login_successful()
        
        log.info("Valid login test passed")
    
    @pytest.mark.negative
    @pytest.mark.parametrize("username,password,expected_error", [
        ("invalid", "password", "The username and password could not be verified"),
        ("", "password", "Please enter a username and password"),
        ("testuser", "", "Please enter a username and password"),
        ("", "", "Please enter a username and password"),
        ("nonexistent", "wrongpass", "The username and password could not be verified"),
        ("testuser", "wrongpassword", "The username and password could not be verified")
    ])
    def test_invalid_login_scenarios(self, username, password, expected_error):
        """Test various invalid login scenarios."""
        # Act
        self.login_page.login(username, password)
        
        # Assert
        self.login_page.assert_login_failed(expected_error)
        assert not self.login_page.is_login_successful()
        
        log.info(f"Invalid login test passed for: {username}")
    
    @pytest.mark.negative
    @pytest.mark.security
    @pytest.mark.parametrize("malicious_input", security_test_data['xss_payloads'])
    def test_login_xss_protection(self, malicious_input):
        """Test login page XSS protection."""
        # Act
        self.login_page.login(malicious_input, "password123")
        
        # Assert
        # Should not contain script tags in error message or page
        page_content = self.login_page.page.content()
        assert "<script>" not in page_content.lower()
        
        log.info(f"XSS protection test passed for: {malicious_input[:20]}...")
    
    @pytest.mark.negative
    @pytest.mark.security
    @pytest.mark.parametrize("sql_payload", security_test_data['sql_injection_payloads'])
    def test_login_sql_injection_protection(self, sql_payload):
        """Test login page SQL injection protection."""
        # Act
        self.login_page.login(sql_payload, "password123")
        
        # Assert
        # Should not authenticate with SQL injection
        assert not self.login_page.is_login_successful()
        
        log.info(f"SQL injection protection test passed for: {sql_payload[:20]}...")
    
    @pytest.mark.accessibility
    def test_login_page_accessibility(self):
        """Test login page accessibility features."""
        # Act
        accessibility_results = self.login_page.validate_login_form_accessibility()
        
        # Assert
        assert accessibility_results['username_has_label'], "Username field should have label"
        assert accessibility_results['password_has_label'], "Password field should have label"
        assert accessibility_results['login_button_has_text'], "Login button should have text"
        assert accessibility_results['form_is_keyboard_accessible'], "Form should be keyboard accessible"
        
        log.info("Accessibility test passed")
    
    @pytest.mark.ui
    def test_login_page_elements_visibility(self):
        """Test all login page elements are visible."""
        # Assert
        self.login_page.assert_login_page_loaded()
        
        # Additional checks
        assert self.login_page.is_forgot_password_link_visible()
        assert self.login_page.is_register_link_visible()
        assert self.login_page.is_username_field_enabled()
        assert self.login_page.is_password_field_enabled()
        assert self.login_page.is_login_button_enabled()
        
        log.info("Page elements visibility test passed")
    
    @pytest.mark.boundary
    @pytest.mark.parametrize("username", boundary_test_data['text_boundaries']['special_chars'])
    def test_username_special_characters(self, username):
        """Test username field with special characters."""
        # Act
        self.login_page.login(username, "Password123!")
        
        # Assert - Should handle gracefully without crashing
        error_message = self.login_page.get_error_message()
        assert len(error_message) > 0 or self.login_page.is_login_successful()
        
        log.info(f"Special characters test passed for: {username}")
    
    @pytest.mark.performance
    def test_login_performance(self, performance_metrics):
        """Test login performance."""
        # Act
        performance_metrics.start_timer("login")
        self.login_page.login("john.doe", "Password123!")
        login_complete = self.login_page.wait_for_login_complete(timeout=5000)
        performance_metrics.end_timer("login")
        
        # Assert
        assert login_complete, "Login should complete within timeout"
        
        # Check performance (should be under 3 seconds)
        login_duration = performance_metrics.get_average("login")
        assert login_duration < 3.0, f"Login took {login_duration}s, should be under 3s"
        
        log.info(f"Login performance test passed: {login_duration:.2f}s")
    
    @pytest.mark.ui
    def test_password_field_masking(self):
        """Test password field is properly masked."""
        # Assert
        assert self.login_page.is_password_field_masked(), "Password field should be masked"
        
        log.info("Password field masking test passed")
    
    @pytest.mark.ui
    def test_login_form_validation(self):
        """Test login form validation states."""
        # Test empty form validation
        self.login_page.clear_login_form()
        form_state = self.login_page.get_form_validation_state()
        
        # Assert
        assert form_state['username_empty'], "Username should be empty"
        assert form_state['password_empty'], "Password should be empty"
        assert form_state['form_visible'], "Form should be visible"
        
        log.info("Form validation test passed")
    
    @pytest.mark.ui
    def test_enter_key_submission(self):
        """Test login submission with Enter key."""
        # Arrange
        self.login_page.enter_username("john.doe")
        self.login_page.enter_password("Password123!")
        
        # Act
        self.login_page.press_enter_in_password_field()
        
        # Assert
        login_complete = self.login_page.wait_for_login_complete()
        assert login_complete, "Login should complete with Enter key"
        
        log.info("Enter key submission test passed")
    
    @pytest.mark.regression
    def test_login_with_retry_mechanism(self):
        """Test login with retry mechanism."""
        # Arrange
        valid_user = user_test_data['valid_user']
        
        # Act
        login_result = self.login_page.login_with_validation(
            valid_user['username'], 
            valid_user['password']
        )
        
        # Assert
        assert login_result['success'], f"Login should succeed: {login_result.get('error_message')}"
        assert 'welcome_message' in login_result, "Should have welcome message"
        
        log.info("Login with retry mechanism test passed")
    
    @pytest.mark.ui
    def test_navigation_links(self):
        """Test navigation links functionality."""
        # Test forgot password link
        self.login_page.click_forgot_password()
        current_url = self.login_page.get_url()
        assert "forgotpassword" in current_url.lower(), "Should navigate to forgot password"
        
        # Navigate back
        self.login_page.goto(f"{get_settings().base_url}/index.htm")
        
        # Test register link
        self.login_page.click_register()
        current_url = self.login_page.get_url()
        assert "register" in current_url.lower(), "Should navigate to register"
        
        log.info("Navigation links test passed")
    
    @pytest.mark.boundary
    def test_login_field_boundaries(self, boundary_test_data):
        """Test login field boundary conditions."""
        # Test very long username
        long_username = "a" * 300
        self.login_page.login(long_username, "Password123!")
        
        # Should handle gracefully without crashing
        page_content = self.login_page.page.content()
        assert len(page_content) > 0, "Page should load without crashing"
        
        log.info("Login field boundaries test passed")
    
    @pytest.mark.ui
    def test_welcome_message_content(self):
        """Test welcome message content after successful login."""
        # Arrange
        valid_user = user_test_data['valid_user']
        
        # Act
        self.login_page.login(valid_user['username'], valid_user['password'])
        
        # Assert
        welcome_message = self.login_page.get_welcome_message()
        assert "Welcome" in welcome_message, "Should contain Welcome"
        assert valid_user['username'] in welcome_message, "Should contain username"
        
        log.info("Welcome message content test passed")
    
    @pytest.mark.ui
    def test_login_button_state(self):
        """Test login button state changes."""
        # Initially should be enabled
        assert self.login_page.is_login_button_enabled(), "Login button should be enabled"
        
        # Test button text
        button_text = self.login_page.get_login_button_text()
        assert "log in" in button_text.lower(), "Button should have Login text"
        
        log.info("Login button state test passed")


@pytest.mark.ui
@pytest.mark.login
@pytest.mark.smoke
@pytest.mark.parallel
class TestLoginParallel:
    """Parallel login tests for performance testing."""
    
    def test_parallel_login_performance(self, page: Page, performance_metrics):
        """Test login performance under parallel execution."""
        # Setup
        login_page = LoginPage(page)
        login_page.navigate_to_login()
        
        # Act
        performance_metrics.start_timer("parallel_login")
        login_page.login("john.doe", "Password123!")
        login_complete = login_page.wait_for_login_complete()
        performance_metrics.end_timer("parallel_login")
        
        # Assert
        assert login_complete, "Parallel login should complete"
        
        log.info("Parallel login performance test passed")


@pytest.mark.ui
@pytest.mark.login
@pytest.mark.mobile
class TestLoginMobile:
    """Mobile-specific login tests."""
    
    def test_mobile_login_responsive(self, mobile_page: Page):
        """Test login on mobile viewport."""
        # Setup
        login_page = LoginPage(mobile_page)
        login_page.navigate_to_login()
        
        # Act
        login_page.login("john.doe", "Password123!")
        
        # Assert
        assert login_page.is_login_successful(), "Mobile login should work"
        
        log.info("Mobile login test passed")
