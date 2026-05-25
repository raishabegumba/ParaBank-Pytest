"""
Mobile tests for ParaBank Loan Request page.

Covers responsive layout, touch-friendly visibility, and form usability
across mobile and tablet viewports. Uses Playwright's viewport API to
simulate device dimensions without requiring separate device fixtures.
"""
import pytest
from playwright.sync_api import Page
from src.pages.loan_request_page import LoanRequestPage
from src.pages.login_page import LoginPage
from src.utils.test_data_utils import TestDataUtils
from src.config.logger import log


# Viewport presets used across this module
VIEWPORTS = {
    "mobile_s":  {"width": 375,  "height": 667},   # iPhone SE
    "mobile_l":  {"width": 414,  "height": 896},   # iPhone XR
    "tablet":    {"width": 768,  "height": 1024},  # iPad
    "desktop":   {"width": 1920, "height": 1080},  # Full HD baseline
}


@pytest.mark.ui
@pytest.mark.loan_request
@pytest.mark.mobile
class TestLoanRequestMobile:
    """Mobile and responsive tests — form visibility and usability across device sizes."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.page = page
        self.loan_page = LoanRequestPage(page)
        self.login_page = LoginPage(page)
        self.test_data = TestDataUtils()

    def login_and_navigate(self):
        """Login and land on the loan request page."""
        self.login_page.navigate_to_login()
        result = self.login_page.login_with_validation("john", "demo")
        assert result['success'], "Login should be successful"
        self.loan_page.navigate_to_loan_request()
        self.loan_page.assert_loan_request_page_loaded()

    def _assert_form_visible(self, label: str):
        """Assert all core form elements are visible at the current viewport."""
        assert self.page.is_visible(self.loan_page.LOAN_AMOUNT_FIELD), \
            f"Loan amount field not visible at {label}"
        assert self.page.is_visible(self.loan_page.DOWN_PAYMENT_FIELD), \
            f"Down payment field not visible at {label}"
        assert self.page.is_visible(self.loan_page.FROM_ACCOUNT_SELECT), \
            f"From account select not visible at {label}"
        assert self.page.is_visible(self.loan_page.APPLY_FOR_LOAN_BUTTON), \
            f"Apply button not visible at {label}"

    # ------------------------------------------------------------------ #
    #  Visibility across viewports                                         #
    # ------------------------------------------------------------------ #

    @pytest.mark.responsive
    def test_form_visible_on_mobile_small(self):
        """All form elements are visible on a small mobile viewport (375×667)."""
        self.login_and_navigate()
        self.page.set_viewport_size(VIEWPORTS["mobile_s"])
        self._assert_form_visible("375×667 (mobile S)")

    @pytest.mark.responsive
    def test_form_visible_on_mobile_large(self):
        """All form elements are visible on a large mobile viewport (414×896)."""
        self.login_and_navigate()
        self.page.set_viewport_size(VIEWPORTS["mobile_l"])
        self._assert_form_visible("414×896 (mobile L)")

    @pytest.mark.responsive
    def test_form_visible_on_tablet(self):
        """All form elements are visible on a tablet viewport (768×1024)."""
        self.login_and_navigate()
        self.page.set_viewport_size(VIEWPORTS["tablet"])
        self._assert_form_visible("768×1024 (tablet)")

    @pytest.mark.responsive
    def test_form_visible_on_desktop(self):
        """All form elements are visible on a desktop viewport (1920×1080)."""
        self.login_and_navigate()
        self.page.set_viewport_size(VIEWPORTS["desktop"])
        self._assert_form_visible("1920×1080 (desktop)")

    # ------------------------------------------------------------------ #
    #  Functional usability on mobile                                      #
    # ------------------------------------------------------------------ #

    @pytest.mark.responsive
    def test_form_fillable_on_mobile(self):
        """Form can be filled and submitted on a mobile viewport."""
        self.login_and_navigate()
        self.page.set_viewport_size(VIEWPORTS["mobile_s"])

        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            self.loan_page.select_from_account(accounts[0])
            self.loan_page.enter_loan_amount("10000.00")
            self.loan_page.enter_down_payment("1000.00")

            validation = self.loan_page.validate_loan_request_form()
            assert validation['form_ready'], \
                "Form should be fillable and ready on mobile viewport"

    @pytest.mark.responsive
    def test_loan_submission_on_tablet(self):
        """A loan application submitted on a tablet viewport completes processing."""
        self.login_and_navigate()
        self.page.set_viewport_size(VIEWPORTS["tablet"])

        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            self.loan_page.apply_for_loan("10000.00", "1000.00", accounts[0])
            assert self.loan_page.wait_for_loan_processing_complete(), \
                "Loan processing should complete on tablet viewport"
            result = self.loan_page.is_loan_approved() or self.loan_page.is_loan_denied()
            assert result, "Should receive approval or denial on tablet"

    # ------------------------------------------------------------------ #
    #  Viewport switching                                                  #
    # ------------------------------------------------------------------ #

    @pytest.mark.responsive
    def test_form_remains_functional_after_viewport_switch(self):
        """Form remains functional when viewport changes."""

        self.page.set_viewport_size(VIEWPORTS["desktop"])
        self.login_and_navigate()

        self._assert_form_visible("desktop")

        self.page.set_viewport_size(VIEWPORTS["mobile_s"])
        self._assert_form_visible("mobile")

        accounts = self.loan_page.get_available_accounts()

        if len(accounts) > 0:
            self.loan_page.enter_loan_amount("5000.00")

            loan_val = self.page.locator(
                self.loan_page.LOAN_AMOUNT_FIELD
            ).input_value()

            assert loan_val == "5000.00"

    # ------------------------------------------------------------------ #
    #  Localization / content on mobile                                    #
    # ------------------------------------------------------------------ #

    @pytest.mark.localization
    def test_page_content_and_labels_on_mobile(self):
        """Page content and form labels render correctly on mobile."""
        
        self.page.set_viewport_size(VIEWPORTS["mobile_s"])
        self.login_and_navigate()

        assert len(self.page.content()) > 0, \
            "Page should have content on mobile"

        assert self.page.locator("text=Loan Amount").is_visible()
        assert self.page.locator("text=Down Payment").is_visible()
        assert self.page.locator("text=From Account").is_visible()

        log.info("Loan form text labels verified on mobile")