import pytest
from src.pages.registration_page import RegistrationPage
from src.utils.registration_helpers import RegistrationHelpers
from test_data.registration_data import get_valid_user


@pytest.mark.smoke
class TestRegistrationSmoke:

    def test_valid_registration(self, page):
        reg = RegistrationPage(page)

        user = get_valid_user()
        RegistrationHelpers.register_user(reg, user)

        assert reg.is_registration_successful()
        assert "Welcome" in reg.get_success_message()