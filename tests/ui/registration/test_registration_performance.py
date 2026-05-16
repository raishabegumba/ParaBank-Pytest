import time
import pytest
from src.pages.registration_page import RegistrationPage
from src.utils.registration_helpers import RegistrationHelpers
from test_data.registration_data import get_valid_user


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