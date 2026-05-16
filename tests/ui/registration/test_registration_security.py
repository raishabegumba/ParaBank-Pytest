import pytest
from src.pages.registration_page import RegistrationPage
from src.utils.registration_helpers import RegistrationHelpers
from src.fixtures.test_data_fixtures import security_test_data
from test_data.registration_data import get_valid_user


@pytest.mark.security
class TestRegistrationSecurity:

    @pytest.mark.parametrize("payload", security_test_data["xss_payloads"])
    def test_xss_protection(self, page, payload):
        reg = RegistrationPage(page)

        user = get_valid_user()
        user["first_name"] = payload

        RegistrationHelpers.register_user(reg, user)

        assert "<script>" not in page.content().lower()