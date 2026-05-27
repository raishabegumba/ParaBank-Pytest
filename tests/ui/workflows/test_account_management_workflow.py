"""
==============================================================================
Account Management Workflow Tests
==============================================================================

Feature: Account Management
Story:   Authenticated user opens accounts and manages their profile

Covers:
    - Open a new CHECKING account and verify the account count increases
    - Open a new SAVINGS account and verify the account count increases
    - Open multiple accounts in sequence and verify cumulative count
    - Accounts overview data integrity after account creation
    - Profile phone number update and persistence after re-login

ParaBank behaviour confirmed from logs:
    - logged_in_page lands on http://localhost:8080/parabank (base URL),
      NOT overview.htm. Every test must call _go_to_overview() before
      interacting with the accounts table or left-panel nav links.
    - Left-panel nav links (Open New Account etc.) are absent on the base
      URL — they only appear after overview.htm has fully loaded.
    - OpenAccountPage.navigate_to_open_account() uses an absolute URL
      (http://localhost:8080/parabank/openaccount.htm) — this is the only
      reliable way to reach the page without depending on the nav link.
    - is_account_opened_successfully() checks for "Account Opened" in
      page.content() — no separate account ID extractor exists in the PO.
    - simulate_account_opening_with_validation() is the intended full-flow
      method and returns {"success": bool, "error_message": str|None}.

Test data:
    - Account types: account_test_data["account_types"] → ["CHECKING", "SAVINGS"]
    - Profile phone: user_test_data["valid_user"]["phone"] → "555-123-4567"
    - Re-login:      settings.test_username / settings.test_password

Page objects used:
    - AccountsOverviewPage  (src/pages/accounts_overview_page.py)
    - OpenAccountPage       (src/pages/open_account_page.py)
    - LoginPage             (src/pages/login_page.py)
==============================================================================
"""

import pytest
import allure
from playwright.sync_api import Page

from src.pages.accounts_overview_page import AccountsOverviewPage
from src.pages.open_account_page import OpenAccountPage
from src.pages.login_page import LoginPage
from src.config.settings import get_settings
from src.config.logger import log

settings = get_settings()


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _go_to_overview(page: Page) -> AccountsOverviewPage:
    """Navigate explicitly to overview.htm and wait for the accounts table.

    Must be called at the start of any test that needs the accounts table
    or left-panel nav links — these are absent on the base parabank URL
    that logged_in_page lands on.

    Args:
        page: Active Playwright Page instance.

    Returns:
        AccountsOverviewPage confirmed loaded (accounts table visible).

    Raises:
        AssertionError: If overview.htm does not load within the timeout.
    """
    page.goto(f"{settings.base_url}/overview.htm")
    page.wait_for_load_state("networkidle")
    accounts_page = AccountsOverviewPage(page)
    assert accounts_page.verify_page_loaded(), (
        f"Accounts overview did not load. Current URL: {page.url!r}"
    )
    log.info(f"Overview page loaded. URL: {page.url!r}")
    return accounts_page


def _open_account(
    page: Page,
    account_type: str,
    open_account_page: OpenAccountPage,
) -> dict:
    """Navigate to the open-account page and submit for a given account type.

    Uses OpenAccountPage.navigate_to_open_account() which goes via absolute
    URL — avoids the nav-link timing issue seen in the test logs.

    Uses simulate_account_opening_with_validation() which is the intended
    full-flow method on the page object. It handles select → submit → check
    internally and returns {"success": bool, "error_message": str|None}.

    Args:
        page:              Active Playwright Page instance.
        account_type:      "CHECKING" or "SAVINGS" — must match an option
                           label in the #type select element.
        open_account_page: Initialised OpenAccountPage instance.

    Returns:
        Result dict from simulate_account_opening_with_validation():
            {"success": True, "error_message": None}  on success
            {"success": False, "error_message": str}  on failure

    Raises:
        AssertionError: If no source accounts are available to fund the new
                        account, or if the page fails to load.
    """
    # Navigate via absolute URL — reliable regardless of nav-link state
    open_account_page.navigate_to_open_account()

    source_accounts = open_account_page.get_source_accounts()
    assert len(source_accounts) > 0, (
        "No source accounts available to fund the new account. "
        "The test user must have at least one existing account with funds. "
        f"Account type requested: {account_type!r}"
    )

    result = open_account_page.simulate_account_opening_with_validation(
        account_type=account_type,
        source_account=source_accounts[0],
    )
    log.info(
        f"Account opening result for {account_type!r}: "
        f"success={result['success']}, error={result['error_message']!r}"
    )
    return result


# ---------------------------------------------------------------------------
# Test suite
# ---------------------------------------------------------------------------

@allure.feature("Workflow Tests")
@allure.story("Account Management")
class TestAccountManagementWorkflow:
    """End-to-end workflow tests for account management features.

    All tests navigate explicitly to the required page via URL because
    logged_in_page lands on the base parabank URL, not overview.htm.
    """

    # -----------------------------------------------------------------------
    # Test 1 — Open a new CHECKING account
    # -----------------------------------------------------------------------

    @pytest.mark.workflow
    @pytest.mark.e2e
    @pytest.mark.critical
    @allure.title("Open New Checking Account Workflow")
    def test_open_new_checking_account_workflow(
        self,
        logged_in_page: Page,
        account_test_data,
    ):
        """Verify a new CHECKING account can be opened and the count increases.

        Steps:
            1. Navigate to overview.htm and record the baseline account count.
            2. Navigate to openaccount.htm via absolute URL and submit CHECKING.
            3. Assert simulate_account_opening_with_validation() returns success.
            4. Return to overview.htm and assert count increased by exactly 1.

        Data: account_test_data["account_types"][0] → "CHECKING"
        """
        page = logged_in_page
        open_account_page = OpenAccountPage(page)

        account_type = account_test_data["account_types"][0]  # "CHECKING"

        # Step 1 — Baseline count before opening any account
        with allure.step("Navigate to overview and record baseline account count"):
            accounts_page = _go_to_overview(page)
            initial_count = accounts_page.get_account_count()
            log.info(f"Baseline account count: {initial_count}")

        # Steps 2 & 3 — Navigate to open-account page and submit
        with allure.step(f"Open new {account_type} account"):
            result = _open_account(page, account_type, open_account_page)

            assert result["success"], (
                f"Expected account opening to succeed for type {account_type!r}. "
                f"Error: {result['error_message']!r}. "
                f"'Account Opened' not found in page content."
            )

        # Step 4 — Verify the table reflects the new account
        with allure.step("Verify account count increased by 1 on overview page"):
            accounts_page = _go_to_overview(page)
            new_count = accounts_page.get_account_count()

            assert new_count == initial_count + 1, (
                f"Expected account count to go from {initial_count} to "
                f"{initial_count + 1}, got {new_count}"
            )
            log.info(
                f"CHECKING account verified. "
                f"Count: {initial_count} → {new_count}"
            )

    # -----------------------------------------------------------------------
    # Test 2 — Open a new SAVINGS account
    # -----------------------------------------------------------------------

    @pytest.mark.workflow
    @pytest.mark.e2e
    @allure.title("Open New Savings Account Workflow")
    def test_open_new_savings_account_workflow(
        self,
        logged_in_page: Page,
        account_test_data,
    ):
        """Verify a new SAVINGS account can be opened and the count increases.

        Mirrors the CHECKING test using account_types[1] → "SAVINGS".
        Confirms the account type selector works for the second dropdown
        option and that the overview count updates correctly.

        Data: account_test_data["account_types"][1] → "SAVINGS"
        """
        page = logged_in_page
        open_account_page = OpenAccountPage(page)

        account_type = account_test_data["account_types"][1]  # "SAVINGS"

        with allure.step("Navigate to overview and record baseline account count"):
            accounts_page = _go_to_overview(page)
            initial_count = accounts_page.get_account_count()
            log.info(f"Baseline account count: {initial_count}")

        with allure.step(f"Open new {account_type} account"):
            result = _open_account(page, account_type, open_account_page)

            assert result["success"], (
                f"Expected account opening to succeed for type {account_type!r}. "
                f"Error: {result['error_message']!r}. "
                f"'Account Opened' not found in page content."
            )

        with allure.step("Verify account count increased by 1 on overview page"):
            accounts_page = _go_to_overview(page)
            new_count = accounts_page.get_account_count()

            assert new_count == initial_count + 1, (
                f"Expected account count to go from {initial_count} to "
                f"{initial_count + 1}, got {new_count}"
            )
            log.info(
                f"SAVINGS account verified. "
                f"Count: {initial_count} → {new_count}"
            )

    # -----------------------------------------------------------------------
    # Test 3 — Open both account types in sequence
    # -----------------------------------------------------------------------

    @pytest.mark.workflow
    @pytest.mark.e2e
    @allure.title("Open Multiple Accounts In Sequence")
    def test_open_multiple_accounts_in_sequence(
        self,
        logged_in_page: Page,
        account_test_data,
    ):
        """Verify two accounts can be opened back-to-back.

        Opens one CHECKING and one SAVINGS in the same test to confirm:
            - The open-account page loads cleanly on each navigation.
            - The overview count increases by 1 after each submission.
            - The cumulative count is baseline + 2 after both are opened.

        Steps:
            1. Record the baseline count.
            2. Open CHECKING — assert count is baseline + 1.
            3. Open SAVINGS  — assert count is baseline + 2.

        Data: account_test_data["account_types"] → ["CHECKING", "SAVINGS"]
        """
        page = logged_in_page
        open_account_page = OpenAccountPage(page)

        with allure.step("Record baseline account count"):
            accounts_page = _go_to_overview(page)
            initial_count = accounts_page.get_account_count()
            log.info(f"Baseline account count: {initial_count}")

        for i, account_type in enumerate(
            account_test_data["account_types"], start=1
        ):
            with allure.step(f"Open {account_type} account ({i} of 2)"):
                result = _open_account(page, account_type, open_account_page)

                assert result["success"], (
                    f"Expected account opening to succeed for {account_type!r} "
                    f"(iteration {i}). "
                    f"Error: {result['error_message']!r}"
                )

            with allure.step(
                f"Verify overview count after opening account {i}"
            ):
                accounts_page = _go_to_overview(page)
                current_count = accounts_page.get_account_count()
                expected = initial_count + i

                assert current_count == expected, (
                    f"After opening {i} account(s), expected count {expected}, "
                    f"got {current_count}. "
                    f"Account type that was just opened: {account_type!r}"
                )
                log.info(
                    f"Count after opening {account_type}: "
                    f"{current_count} (expected {expected})"
                )

        log.info(
            f"Both accounts opened successfully. "
            f"Final count: {initial_count + 2}"
        )

    # -----------------------------------------------------------------------
    # Test 4 — Accounts overview data integrity
    # -----------------------------------------------------------------------

    @pytest.mark.workflow
    @pytest.mark.e2e
    @allure.title("Accounts Overview Data Integrity")
    def test_accounts_overview_data_integrity(
        self,
        logged_in_page: Page,
    ):
        """Verify all accounts in the overview table have valid, parseable data.

        Uses AccountsOverviewPage.validate_account_data_integrity() to check:
            - Every row has a non-empty account ID
            - Every row has a balance in parseable ($X.XX) format
            - Every row has a non-empty available amount
            - No duplicate account IDs exist
            - Total balance can be calculated from the individual row balances

        Does not open any accounts — validates the test user's existing
        accounts as they stand after the logged_in_page fixture authenticated.
        """
        page = logged_in_page

        with allure.step("Navigate to overview and confirm accounts exist"):
            accounts_page = _go_to_overview(page)
            assert accounts_page.has_accounts(), (
                "Test user has no accounts — cannot validate data integrity. "
                "Ensure the test user has at least one account."
            )
            account_count = accounts_page.get_account_count()
            log.info(
                f"Validating data integrity for {account_count} account(s)"
            )

        with allure.step("Run data integrity validation on all accounts"):
            validation = accounts_page.validate_account_data_integrity()
            issues = validation.get("issues_found", [])

            log.info(f"Validation results: {validation}")

            assert validation["all_accounts_have_ids"], (
                f"Some accounts are missing IDs. Issues: {issues}"
            )
            assert validation["all_accounts_have_balances"], (
                f"Some accounts are missing balances. Issues: {issues}"
            )
            assert validation["all_accounts_have_available_amounts"], (
                f"Some accounts are missing available amounts. Issues: {issues}"
            )
            assert validation["balance_format_valid"], (
                f"Some balances are not in parseable format. Issues: {issues}"
            )
            assert not validation["duplicate_accounts"], (
                f"Duplicate account IDs found. Issues: {issues}"
            )
            assert validation["total_balance_calculable"], (
                f"Could not calculate total balance from rows. Issues: {issues}"
            )
            assert len(issues) == 0, (
                f"Data integrity issues found: {issues}"
            )
            log.info(
                f"Data integrity validated for {account_count} account(s). "
                f"Calculated total: {validation.get('calculated_total')}"
            )

    # -----------------------------------------------------------------------
    # Test 5 — Profile phone update persists after re-login
    # -----------------------------------------------------------------------

    @pytest.mark.workflow
    @pytest.mark.e2e
    @allure.title("Profile Phone Update Persists After Re-Login")
    def test_profile_update_phone_persists(
        self,
        logged_in_page: Page,
        user_test_data,
    ):
        """Verify a profile phone update is saved and survives logout/login.

        Steps:
            1. Navigate to /updateprofile.htm and update the phone field.
            2. Submit and assert the confirmation heading contains 'updated'.
            3. Navigate to overview.htm and log out cleanly.
            4. Log back in with settings.test_username / test_password.
            5. Navigate to /updateprofile.htm and read the phone field value.
            6. Assert the saved value matches what was submitted in step 1.

        Data:
            new_phone → user_test_data["valid_user"]["phone"] ("555-123-4567")
            re-login  → settings.test_username / settings.test_password
        """
        page = logged_in_page
        login_page = LoginPage(page)

        # Static valid_user phone — guaranteed clean "###-###-####" format
        new_phone = user_test_data["valid_user"]["phone"]  # "555-123-4567"

        phone_selector = "#customer\\.phoneNumber"
        submit_selector = "input[type='submit'], input[type='button'], button"  # broader match for submit controls
        success_selector = "#rightPanel .title"

        # Steps 1 & 2 — Update the phone number and assert confirmation
        with allure.step(f"Update profile phone to: {new_phone!r}"):
            page.goto(f"{settings.base_url}/updateprofile.htm")
            page.wait_for_load_state("networkidle")

            assert page.locator(phone_selector).count() > 0, (
                "Phone field (#customer\\.phoneNumber) not found on "
                "/updateprofile.htm — confirm the user is logged in. "
                f"URL: {page.url!r}"
            )
            page.locator(phone_selector).fill(new_phone)

            assert page.locator(submit_selector).count() > 0, (
                "Update Profile submit button not found on /updateprofile.htm. "
                f"URL: {page.url!r}"
            )
            page.locator(submit_selector).first.click()
            page.wait_for_load_state("networkidle")

            # ParaBank renders a "Profile Updated" heading on success
            elements = page.locator(success_selector)
            assert elements.count() > 0, (
                "No confirmation heading found after submitting profile update. "
                f"URL: {page.url!r}"
            )
            confirmation_text = ""
            for i in range(elements.count()):
                text = (elements.nth(i).text_content() or "")
                if "updated" in text.lower():
                    confirmation_text = text
                    break
            assert "updated" in confirmation_text.lower(), (
                f"Expected 'updated' in confirmation heading, got: {confirmation_text!r}"
            )
            log.info(f"Profile phone updated to {new_phone!r}")

        # Step 3 — End the session cleanly via the accounts overview page
        with allure.step("Navigate to overview and log out"):
            accounts_page = _go_to_overview(page)
            accounts_page.logout()
            page.wait_for_load_state("networkidle")
            log.info("Logged out successfully")

        # Step 4 — Re-authenticate with the same credentials
        with allure.step(f"Log back in as: {settings.test_username!r}"):
            login_page.navigate_to_login()
            login_page.login(
                username=settings.test_username,
                password=settings.test_password,
            )
            login_page.wait_for_login_complete()
            login_page.assert_login_successful()
            log.info(f"Re-logged in as: {settings.test_username!r}")

        # Steps 5 & 6 — Confirm the submitted phone value survived the session
        with allure.step("Verify updated phone persists on profile page"):
            page.goto(f"{settings.base_url}/updateprofile.htm")
            page.wait_for_load_state("networkidle")

            assert page.locator(phone_selector).count() > 0, (
                "Phone field not found on /updateprofile.htm after re-login. "
                f"URL: {page.url!r}"
            )
            saved_phone = page.locator(phone_selector).input_value()

            assert saved_phone == new_phone, (
                f"Phone did not persist after re-login. "
                f"Expected: {new_phone!r}, got: {saved_phone!r}"
            )
            log.info(
                f"Phone persistence confirmed: {saved_phone!r} "
                f"matches submitted value {new_phone!r}"
            )