"""
==============================================================================
User Onboarding Workflow Tests
==============================================================================

ParaBank behaviour confirmed from logs:
- Successful registration shows: "Welcome {username}" + "Your account was
  created successfully. You are now logged in."
- The user IS auto-logged-in after registration — no manual login step needed.
- overview.htm is reachable immediately after registration succeeds.
==============================================================================
"""

import pytest
import allure
from playwright.sync_api import Page

from src.pages.registration_page import RegistrationPage
from src.pages.login_page import LoginPage
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.config.logger import log


def _assert_registration_success(message: str, username: str) -> None:
    """
    Central success assertion used by every test that expects registration
    to succeed. Keeps the expected strings in one place so a future ParaBank
    build change only requires editing here.

    Confirmed actual message from logs:
        'Welcome {username} Your account was created successfully. You are now logged in.'
    """
    lower = message.lower()
    assert "welcome" in lower, (
        f"Expected 'Welcome' in success message, got: {message!r}"
    )
    assert "account was created successfully" in lower, (
        f"Expected 'account was created successfully' in success message, "
        f"got: {message!r}"
    )
    assert username.lower() in lower, (
        f"Expected username {username!r} in success message, got: {message!r}"
    )


@allure.feature("Workflow Tests")
@allure.story("User Onboarding")
class TestUserOnboardingWorkflow:

    @pytest.mark.workflow
    @pytest.mark.e2e
    @pytest.mark.critical
    @allure.title("Complete Registration and Login Workflow")
    def test_registration_and_login_workflow(
        self,
        page: Page,
        user_test_data,
    ):
        """
        Full onboarding flow: register a new user, verify the auto-login
        success screen, then confirm the accounts overview page is accessible.

        ParaBank auto-logs-in the user after registration and shows:
        'Welcome {username} Your account was created successfully. You are now logged in.'
        No manual login step is required.
        """
        registration_page = RegistrationPage(page)
        accounts_page = AccountsOverviewPage(page)

        data = user_test_data["random_users"][0]

        with allure.step("Navigate to registration page"):
            registration_page.navigate_to_registration()
            registration_page.assert_registration_page_loaded()
            log.info("Registration page loaded and verified")

        with allure.step(f"Register new user: {data['username']}"):
            registration_page.complete_registration(
                first_name=data["first_name"],
                last_name=data["last_name"],
                address=data["address"],
                city=data["city"],
                state=data["state"],
                zip_code=data["zip_code"],
                phone=data["phone"],
                ssn=data["ssn"],
                username=data["username"],
                password=data["password"],
                confirm_password=data["password"],
            )
            log.info(f"Registration form submitted for: {data['username']}")

        with allure.step("Verify registration success and auto-login"):
            registration_page.wait_for_registration_complete()
            success_message = registration_page.get_success_message()

            assert success_message != "", (
                f"Expected a success message after registration, got empty string. "
                f"URL: {page.url!r}"
            )
            _assert_registration_success(success_message, data["username"])
            log.info(f"Registration + auto-login confirmed: {success_message!r}")

        with allure.step("Verify accounts overview page accessible after auto-login"):
            # User is already logged in — navigate directly to overview
            page.goto(f"{page.url.split('/parabank')[0]}/parabank/overview.htm")
            assert accounts_page.verify_page_loaded(), (
                f"Accounts overview page did not load after auto-login. "
                f"URL: {page.url!r}"
            )
            log.info("Accounts overview page verified — onboarding workflow complete")

    @pytest.mark.workflow
    @pytest.mark.e2e
    @allure.title("Registration With Valid User Data")
    def test_registration_with_valid_user(
        self,
        page: Page,
        user_test_data,
    ):
        """
        Register using random_users[1]. Verifies the success screen only.
        Uses slot [1] to avoid username collision with the workflow test.
        """
        registration_page = RegistrationPage(page)
        data = user_test_data["random_users"][1]

        with allure.step("Navigate to registration page"):
            registration_page.navigate_to_registration()
            registration_page.assert_registration_page_loaded()

        with allure.step(f"Submit registration form for: {data['username']}"):
            registration_page.complete_registration(
                first_name=data["first_name"],
                last_name=data["last_name"],
                address=data["address"],
                city=data["city"],
                state=data["state"],
                zip_code=data["zip_code"],
                phone=data["phone"],
                ssn=data["ssn"],
                username=data["username"],
                password=data["password"],
                confirm_password=data["password"],
            )

        with allure.step("Verify registration success screen"):
            registration_page.wait_for_registration_complete()
            success_message = registration_page.get_success_message()

            assert success_message != "", (
                f"No success message shown. URL: {page.url!r}"
            )
            _assert_registration_success(success_message, data["username"])
            log.info(f"Registration verified for: {data['username']!r}")

    @pytest.mark.workflow
    @pytest.mark.e2e
    @allure.title("Registration Fails With Duplicate Username")
    def test_registration_fails_with_duplicate_username(
        self,
        page: Page,
        user_test_data,
    ):
        """
        Register valid_user twice. Second attempt must show an error.
        Uses the static valid_user entry so the username is predictable.
        """
        registration_page = RegistrationPage(page)
        data = user_test_data["valid_user"]

        with allure.step("First registration — should succeed"):
            registration_page.navigate_to_registration()
            registration_page.complete_registration(
                first_name=data["first_name"],
                last_name=data["last_name"],
                address=data["address"],
                city=data["city"],
                state=data["state"],
                zip_code=data["zip_code"],
                phone=data["phone"],
                ssn=data["ssn"],
                username=data["username"],
                password=data["password"],
                confirm_password=data["password"],
            )
            registration_page.wait_for_registration_complete()
            first_message = registration_page.get_success_message()
            _assert_registration_success(first_message, data["username"])
            log.info("First registration succeeded as expected")

        with allure.step("Second registration with same username — should fail"):
            registration_page.navigate_to_registration()
            registration_page.complete_registration(
                first_name=data["first_name"],
                last_name=data["last_name"],
                address=data["address"],
                city=data["city"],
                state=data["state"],
                zip_code=data["zip_code"],
                phone=data["phone"],
                ssn=data["ssn"],
                username=data["username"],
                password=data["password"],
                confirm_password=data["password"],
            )
            registration_page.wait_for_registration_complete()

            error_message = registration_page.get_error_message()
            assert error_message != "", (
                "Expected an error for duplicate username, got empty error message. "
                f"Success message shown instead: "
                f"{registration_page.get_success_message()!r}"
            )
            log.info(f"Duplicate username correctly rejected: {error_message!r}")

    @pytest.mark.workflow
    @pytest.mark.e2e
    @allure.title("Registration Fails With Mismatched Passwords")
    def test_registration_fails_with_mismatched_passwords(
        self,
        page: Page,
        user_test_data,
    ):
        """
        Submit the form with confirm_password different from password.
        Expects a validation error. Uses random_users[2].
        """
        registration_page = RegistrationPage(page)
        data = user_test_data["random_users"][2]

        with allure.step("Navigate to registration page"):
            registration_page.navigate_to_registration()
            registration_page.assert_registration_page_loaded()

        with allure.step("Submit form with mismatched passwords"):
            registration_page.complete_registration(
                first_name=data["first_name"],
                last_name=data["last_name"],
                address=data["address"],
                city=data["city"],
                state=data["state"],
                zip_code=data["zip_code"],
                phone=data["phone"],
                ssn=data["ssn"],
                username=data["username"],
                password=data["password"],
                confirm_password=data["password"] + "_mismatch",
            )

        with allure.step("Verify password mismatch error is shown"):
            registration_page.wait_for_registration_complete()
            error_message = registration_page.get_error_message()
            assert error_message != "", (
                "Expected a validation error for mismatched passwords, "
                "got empty error message"
            )
            log.info(f"Password mismatch correctly rejected: {error_message!r}")

    @pytest.mark.workflow
    @pytest.mark.e2e
    @allure.title("Login Fails With Invalid Credentials")
    def test_login_fails_with_invalid_credentials(
        self,
        page: Page,
        user_test_data,
    ):
        """
        Attempt login with the invalid_user credentials.
        Expects an error message and no redirect to overview.htm.
        """
        login_page = LoginPage(page)
        data = user_test_data["invalid_user"]

        with allure.step("Navigate to login page"):
            login_page.navigate_to_login()
            login_page.assert_login_page_loaded()

        with allure.step(f"Attempt login with invalid credentials: {data['username']}"):
            login_page.login(
                username=data["username"],
                password=data["password"],
            )
            login_page.wait_for_login_complete()

        with allure.step("Verify login failure error is shown"):
            assert not login_page.is_login_successful(), (
                "Login should have failed but is_login_successful() returned True"
            )
            error_message = login_page.get_error_message()
            assert error_message != "", (
                "Expected an error message for invalid credentials, got empty string"
            )
            log.info(f"Invalid login correctly rejected: {error_message!r}")

    @pytest.mark.workflow
    @pytest.mark.e2e
    @allure.title("Registered User Can Log In and Log Out")
    def test_registered_user_can_login_and_logout(
        self,
        page: Page,
        user_test_data,
    ):
        """
        Register a fresh user (slot [3]), confirm auto-login success,
        navigate to accounts overview, log out, and verify the session ends.
        """
        registration_page = RegistrationPage(page)
        login_page = LoginPage(page)
        accounts_page = AccountsOverviewPage(page)

        data = user_test_data["random_users"][3]

        with allure.step(f"Register user: {data['username']}"):
            registration_page.navigate_to_registration()
            registration_page.complete_registration(
                first_name=data["first_name"],
                last_name=data["last_name"],
                address=data["address"],
                city=data["city"],
                state=data["state"],
                zip_code=data["zip_code"],
                phone=data["phone"],
                ssn=data["ssn"],
                username=data["username"],
                password=data["password"],
                confirm_password=data["password"],
            )
            registration_page.wait_for_registration_complete()
            success_message = registration_page.get_success_message()
            _assert_registration_success(success_message, data["username"])
            log.info(f"Registration + auto-login confirmed for: {data['username']!r}")

        with allure.step("Navigate to accounts overview (user already logged in)"):
            base = page.url.split("/parabank")[0]
            page.goto(f"{base}/parabank/overview.htm")
            assert accounts_page.verify_page_loaded(), (
                f"Accounts overview did not load after auto-login. URL: {page.url!r}"
            )

        with allure.step("Log out"):
            accounts_page.logout()
            page.wait_for_load_state("networkidle")

        with allure.step("Verify session ended — login page shown"):
            login_page.assert_login_page_loaded()
            log.info("Logout verified — login page shown after session end")