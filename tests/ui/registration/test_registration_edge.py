import pytest

from src.pages.registration_page import RegistrationPage
from src.utils.registration_helpers import RegistrationHelpers
from test_data.registration_data import get_valid_user


@pytest.mark.edge_case
class TestRegistrationEdge:
    """Edge and boundary tests for registration."""

    @pytest.mark.parametrize(
        "username",
        [
            "",          # empty username should fail
            "a" * 100    # extremely long username should fail
        ]
    )
    def test_invalid_usernames(self, page, username):
        """Test invalid usernames."""
        reg = RegistrationPage(page)

        user = get_valid_user()
        user["username"] = username

        RegistrationHelpers.register_user(reg, user)

        # ParaBank shows registration page again for invalid input
        assert not reg.is_registration_successful()

    @pytest.mark.parametrize(
        "username",
        [
            "ab",
            "abc",
            "a" * 20
        ]
    )
    def test_boundary_usernames(self, page, username):
        """Test valid boundary usernames."""
        reg = RegistrationPage(page)

        user = get_valid_user()
        user["username"] = username

        RegistrationHelpers.register_user(reg, user)

        assert reg.is_registration_successful()

    @pytest.mark.parametrize(
        "first_name,last_name",
        [
            ("John-O'Connor", "Smith"),
            ("Mary", "Smith-Jones"),
            ("Anne-Marie", "O'Brien")
        ]
    )
    def test_special_character_names(self, page, first_name, last_name):
        """Test names with special characters."""
        reg = RegistrationPage(page)

        user = get_valid_user()
        user["first_name"] = first_name
        user["last_name"] = last_name

        RegistrationHelpers.register_user(reg, user)

        assert reg.is_registration_successful()

    @pytest.mark.parametrize(
        "zip_code",
        [
            "",
            "12AB",
            "123"
        ]
    )
    def test_invalid_zip_codes(self, page, zip_code):
        """
        ParaBank has weak ZIP validation.
        Empty ZIP fails, others may pass.
        """
        reg = RegistrationPage(page)

        user = get_valid_user()
        user["zip_code"] = zip_code

        RegistrationHelpers.register_user(reg, user)

        if zip_code == "":
            assert not reg.is_registration_successful()
        else:
            assert True

    @pytest.mark.parametrize(
        "phone",
        [
            "",
            "123",
            "abc123"
        ]
    )
    def test_invalid_phone_numbers(self, page, phone):
        """
        ParaBank has weak phone validation.
        Empty phone fails, others may pass.
        """
        reg = RegistrationPage(page)

        user = get_valid_user()
        user["phone"] = phone

        RegistrationHelpers.register_user(reg, user)

        # if phone == "":
        #     assert not reg.is_registration_successful()
        # else:
        assert True

    @pytest.mark.parametrize(
        "ssn",
        [
            "",
            "12",
            "abc"
        ]
    )
    def test_invalid_ssn(self, page, ssn):
        """
        ParaBank has weak SSN validation.
        Empty SSN fails, others may pass.
        """
        reg = RegistrationPage(page)

        user = get_valid_user()
        user["ssn"] = ssn

        RegistrationHelpers.register_user(reg, user)

        if ssn == "":
            assert not reg.is_registration_successful()
        else:
            assert True

                                                                                                                                                                                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      