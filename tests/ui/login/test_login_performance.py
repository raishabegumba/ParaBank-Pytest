"""Login performance test suite."""
import pytest
from datetime import datetime
from playwright.sync_api import Page
from src.pages.login_page import LoginPage
from src.utils.test_data_utils import TestDataUtils


@pytest.mark.performance
@pytest.mark.login
class TestLoginPerformance:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.login_page = LoginPage(page)
        self.test_data = TestDataUtils()

    def test_login_response_time(self):
        user = self.test_data.get_test_user("john")

        self.login_page.navigate_to_login()

        start = datetime.now()
        result = self.login_page.login_with_validation(
            user["username"],
            user["password"]
        )
        duration = (datetime.now() - start).total_seconds()

        assert result["success"]
        assert duration < 10

    def test_login_page_load_time(self):
        start = datetime.now()
        self.login_page.navigate_to_login()
        duration = (datetime.now() - start).total_seconds()

        assert duration < 5