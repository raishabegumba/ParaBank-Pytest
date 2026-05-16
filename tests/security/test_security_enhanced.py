"""
==============================================================================
Enterprise Security Test Suite - ParaBank
==============================================================================
Senior-level security automation suite covering:
- XSS Prevention
- SQL Injection Prevention
- Session Security
- Authorization Controls
- Cookie Security
- Security Headers
- CSRF Validation
- Unauthorized Access
- Input Validation

Framework:
- Pytest
- Playwright
- Allure Reporting
- Page Object Model

Author: Senior SDET Implementation
"""

import re
import pytest
import allure

from playwright.sync_api import Page, expect

from src.pages.login_page import LoginPage
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.config.settings import settings
from src.config.logger import log


# =============================================================================
# Security Payloads
# =============================================================================

XSS_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert(1)>",
    "javascript:alert('XSS')",
    "<svg/onload=alert(1)>",
]

SQLI_PAYLOADS = [
    "' OR '1'='1",
    "admin'--",
    "' UNION SELECT NULL,NULL--",
    "'; DROP TABLE users--",
]

SQL_ERROR_PATTERNS = [
    "sql syntax",
    "mysql",
    "ora-",
    "sqlite",
    "postgresql",
    "database error",
    "syntax error",
]


# =============================================================================
# Reusable Security Assertions
# =============================================================================

class SecurityAssertions:
    """Reusable enterprise security assertions."""

    @staticmethod
    def assert_no_sql_errors(content: str):
        """Validate no SQL/database errors are exposed."""
        lowered = content.lower()

        for pattern in SQL_ERROR_PATTERNS:
            assert pattern not in lowered, (
                f"Potential SQL error leakage detected: {pattern}"
            )

    @staticmethod
    def assert_not_authenticated(page: Page):
        """Validate user is not authenticated."""
        assert "overview" not in page.url.lower()
        assert "accounts" not in page.title().lower()

    @staticmethod
    def assert_security_headers(response):
        """Validate security headers."""
        headers = response.headers

        expected_headers = [
            "x-frame-options",
            "x-content-type-options",
        ]

        for header in expected_headers:
            assert header in headers, (
                f"Missing security header: {header}"
            )

    @staticmethod
    def assert_secure_cookies(cookies: list):
        """Validate secure cookie configuration."""
        assert cookies, "No cookies found"

        for cookie in cookies:
            assert cookie.get("httpOnly") is True, (
                f"Cookie not HttpOnly: {cookie['name']}"
            )

            if settings.base_url.startswith("https"):
                assert cookie.get("secure") is True, (
                    f"Cookie not Secure: {cookie['name']}"
                )

    @staticmethod
    def assert_no_script_execution(dialog_triggered: bool):
        """Validate no JavaScript execution occurred."""
        assert dialog_triggered is False, (
            "Potential XSS vulnerability detected"
        )


# =============================================================================
# Base Security Test Class
# =============================================================================

class BaseSecurityTest:
    """Shared setup and utilities."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.page = page
        self.login_page = LoginPage(page)

    def navigate_to_login(self):
        """Navigate to login page."""
        self.page.goto(f"{settings.base_url}login.htm")


# =============================================================================
# XSS Prevention Tests
# =============================================================================

@allure.feature("Security")
@allure.story("XSS Prevention")
class TestXSSPrevention(BaseSecurityTest):

    @pytest.mark.security
    @pytest.mark.critical
    @pytest.mark.parametrize("payload", XSS_PAYLOADS)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Validate XSS Prevention")
    def test_xss_payloads_blocked(self, page, payload):
        """
        Verify application safely handles XSS payloads.
        """

        self.navigate_to_login()

        dialog_triggered = False

        def handle_dialog(dialog):
            nonlocal dialog_triggered
            dialog_triggered = True
            dialog.dismiss()

        page.on("dialog", handle_dialog)

        self.login_page.enter_username(payload)
        self.login_page.enter_password("dummy")
        self.login_page.click_login()

        body_content = page.content()

        SecurityAssertions.assert_no_script_execution(
            dialog_triggered
        )

        assert payload not in body_content

        log.info(f"Blocked XSS payload: {payload}")


# =============================================================================
# SQL Injection Tests
# =============================================================================

@allure.feature("Security")
@allure.story("SQL Injection Prevention")
class TestSQLInjection(BaseSecurityTest):

    @pytest.mark.security
    @pytest.mark.critical
    @pytest.mark.parametrize("payload", SQLI_PAYLOADS)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Validate SQL Injection Prevention")
    def test_sql_injection_blocked(
        self,
        page,
        payload
    ):
        """
        Verify SQL injection attempts are blocked.
        """

        self.navigate_to_login()

        self.login_page.login(payload, "invalid")

        page_content = page.content()

        SecurityAssertions.assert_not_authenticated(page)

        SecurityAssertions.assert_no_sql_errors(
            page_content
        )

        assert "welcome" not in page_content.lower()

        log.info(f"Blocked SQL injection payload: {payload}")


# =============================================================================
# Session Security Tests
# =============================================================================

@allure.feature("Security")
@allure.story("Session Security")
class TestSessionSecurity(BaseSecurityTest):

    @pytest.mark.security
    @pytest.mark.critical
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Validate Session Invalidation")
    def test_session_invalidated_after_logout(
        self,
        page,
        test_credentials
    ):
        """
        Verify session becomes invalid after logout.
        """

        accounts_page = AccountsOverviewPage(page)

        self.navigate_to_login()

        self.login_page.login(
            test_credentials["username"],
            test_credentials["password"]
        )

        expect(
            page.locator("text=Accounts Overview")
        ).to_be_visible()

        accounts_page.logout()

        response = page.goto(
            f"{settings.base_url}overview.htm"
        )

        assert response.status in [200, 302, 401, 403]

        SecurityAssertions.assert_not_authenticated(
            page
        )

        log.info("Session invalidation verified")

    @pytest.mark.security
    @allure.title("Validate Unauthorized Access Prevention")
    def test_unauthorized_access_blocked(
        self,
        page
    ):
        """
        Verify protected pages cannot be accessed
        without authentication.
        """

        response = page.goto(
            f"{settings.base_url}overview.htm"
        )

        assert response.status in [200, 302, 401, 403]

        assert (
            "login" in page.url.lower()
            or "sign" in page.content().lower()
        )

        log.info("Unauthorized access correctly blocked")


# =============================================================================
# Cookie Security Tests
# =============================================================================

@allure.feature("Security")
@allure.story("Cookie Security")
class TestCookieSecurity(BaseSecurityTest):

    @pytest.mark.security
    @allure.title("Validate Secure Session Cookies")
    def test_secure_cookie_configuration(
        self,
        page,
        test_credentials
    ):
        """
        Verify cookies are securely configured.
        """

        self.navigate_to_login()

        self.login_page.login(
            test_credentials["username"],
            test_credentials["password"]
        )

        cookies = page.context.cookies()

        SecurityAssertions.assert_secure_cookies(
            cookies
        )

        log.info("Cookie security verified")


# =============================================================================
# Security Header Tests
# =============================================================================

@allure.feature("Security")
@allure.story("Security Headers")
class TestSecurityHeaders(BaseSecurityTest):

    @pytest.mark.security
    @allure.title("Validate Security Headers")
    def test_security_headers_present(
        self,
        page
    ):
        """
        Verify essential security headers exist.
        """

        response = page.goto(
            f"{settings.base_url}login.htm"
        )

        SecurityAssertions.assert_security_headers(
            response
        )

        log.info("Security headers validated")


# =============================================================================
# Authorization Tests
# =============================================================================

@allure.feature("Security")
@allure.story("Authorization")
class TestAuthorizationSecurity(BaseSecurityTest):

    @pytest.mark.security
    @pytest.mark.critical
    @allure.title("Validate Authorization Controls")
    def test_cannot_access_other_user_resources(
        self,
        page,
        test_credentials
    ):
        """
        Verify users cannot access unauthorized resources.
        """

        self.navigate_to_login()

        self.login_page.login(
            test_credentials["username"],
            test_credentials["password"]
        )

        response = page.goto(
            f"{settings.base_url}activity.htm?id=999999"
        )

        assert response.status in [401, 403, 404]

        log.info(
            "Authorization restrictions verified"
        )


# =============================================================================
# Password Security Tests
# =============================================================================

@allure.feature("Security")
@allure.story("Password Security")
class TestPasswordSecurity(BaseSecurityTest):

    @pytest.mark.security
    @allure.title("Validate Password Masking")
    def test_password_field_masked(
        self,
        page
    ):
        """
        Verify password field uses secure masking.
        """

        self.navigate_to_login()

        password_type = page.get_attribute(
            self.login_page.PASSWORD_FIELD,
            "type"
        )

        assert password_type == "password"

        log.info("Password masking verified")

    @pytest.mark.security
    @allure.title("Validate Password Not Exposed")
    def test_password_not_exposed_in_dom(
        self,
        page
    ):
        """
        Verify passwords are not exposed in DOM.
        """

        password = "SecurePassword@123"

        self.navigate_to_login()

        self.login_page.enter_password(password)

        body_content = page.content()

        assert password not in body_content

        log.info("Password exposure check passed")


# =============================================================================
# CSRF Security Tests
# =============================================================================

@allure.feature("Security")
@allure.story("CSRF Protection")
class TestCSRFSecurity(BaseSecurityTest):

    @pytest.mark.security
    @allure.title("Validate CSRF Token Presence")
    def test_csrf_token_present(
        self,
        page
    ):
        """
        Verify CSRF token exists on sensitive forms.
        """

        self.navigate_to_login()

        csrf_token = page.locator(
            "input[name*=csrf]"
        )

        assert (
            csrf_token.count() > 0
            or "csrf" in page.content().lower()
        )

        log.info("CSRF token validation completed")


# =============================================================================
# Input Validation Tests
# =============================================================================

@allure.feature("Security")
@allure.story("Input Validation")
class TestInputValidation(BaseSecurityTest):

    @pytest.mark.security
    @pytest.mark.parametrize(
        "payload",
        [
            "!@#$%^&*()",
            "../../../../etc/passwd",
            "<>",
            "'; DROP TABLE users--",
        ]
    )
    @allure.title("Validate Input Sanitization")
    def test_input_validation(
        self,
        page,
        payload
    ):
        """
        Verify application safely handles malformed input.
        """

        self.navigate_to_login()

        self.login_page.login(payload, payload)

        body_content = page.content()

        SecurityAssertions.assert_no_sql_errors(
            body_content
        )

        assert page.is_visible("body")

        log.info(
            f"Input validation passed for payload: {payload}"
        )