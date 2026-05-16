"""Login edge case test suite."""
import pytest
from playwright.sync_api import Page
from src.pages.login_page import LoginPage
from src.utils.test_data_utils import TestDataUtils


@pytest.mark.ui
@pytest.mark.login
@pytest.mark.edge_case
class TestLoginEdgeCases:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.login_page = LoginPage(page)
        self.test_data = TestDataUtils()
        self.login_page.navigate_to_login()

    def test_login_with_special_characters(self):
        self.login_page.navigate_to_login()
        result = self.login_page.login_with_validation(
            "user@test.com",
            "pass@word#123"
        )
        assert isinstance(result, dict)
        assert "success" in result

    def test_login_with_very_long_credentials(self):
        long_username = "a" * 100
        long_password = "b" * 100

        result = self.login_page.login_with_validation(long_username, long_password)
        assert isinstance(result, dict)
        assert result["success"] is False