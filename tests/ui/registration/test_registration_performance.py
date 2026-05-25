import time
import pytest
from src.pages.registration_page import RegistrationPage
from src.utils.registration_helpers import RegistrationHelpers
from test_data.registration_data import get_valid_user
from datetime import datetime


@pytest.mark.performance
class TestRegistrationPerformance:

    def test_registration_time(self, page):
        reg = RegistrationPage(page)

        user = get_valid_user()

        start = time.time()

        RegistrationHelpers.register_user(reg, user)
        reg.wait_for_registration_complete()

        duration = time.time() - start

        assert duration < 5.0

    @pytest.mark.performance
    def test_registration_page_load_performance(self):
        """Test registration page load performance."""
        start_time = datetime.now()
        self.registration_page.navigate_to_registration()
        self.registration_page.assert_registration_page_loaded()
        load_time = (datetime.now() - start_time).total_seconds()
        
        # Page should load within reasonable time (5 seconds)
        assert load_time < 5.0, f"Page load time {load_time}s exceeds threshold"