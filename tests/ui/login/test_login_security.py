"""Login security test suite."""
import pytest
from playwright.sync_api import Page
from src.pages.login_page import LoginPage


@pytest.mark.ui
@pytest.mark.login
@pytest.mark.security
class TestLoginSecurity:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.login_page = LoginPage(page)
        self.login_page.navigate_to_login()

    @pytest.mark.parametrize("payload,safe_id", [
        ("<script>alert(1)</script>", "xss_script"),
        ("'><img src=x onerror=alert(1)>", "xss_img"),
        ("javascript:alert(1)", "xss_js"),
    ])
    def test_xss_protection(self, payload, safe_id):
        self.login_page.login(payload, "password123")
        content = self.login_page.page.content()
        assert "<script>" not in content.lower()

    @pytest.mark.parametrize("payload,safe_id", [
        ("' OR '1'='1", "sql_1"),
        ("' OR 1=1--", "sql_2"),
        ("admin'--", "sql_admin"),
    ])
    def test_sql_injection_protection(self, payload, safe_id):
        self.login_page.login(payload, "password123")
        assert not self.login_page.is_login_successful()

    def test_login_data_privacy(self):
        self.login_page.navigate_to_login()
        content = self.login_page.page.content()
        assert "password" not in content.lower() or content.count("password") <= 2