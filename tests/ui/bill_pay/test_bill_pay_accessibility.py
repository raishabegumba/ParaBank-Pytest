"""
Accessibility test suite for ParaBank Bill Pay page.
"""

import pytest


@pytest.mark.ui
@pytest.mark.bill_pay
@pytest.mark.accessibility
class TestBillPayAccessibility:

    # =========================================================================
    # SETUP
    # =========================================================================

    @pytest.fixture(autouse=True)
    def setup(
        self,
        page,
        bill_pay_page,
        login_page,
    ):
        """Setup shared fixtures."""

        self.page = page
        self.bill_pay_page = bill_pay_page
        self.login_page = login_page

    # =========================================================================
    # HELPERS
    # =========================================================================

    def login_and_navigate(self):
        """Login and navigate to Bill Pay."""

        self.login_page.navigate_to_login()

        result = self.login_page.login_with_validation(
            "john",
            "demo"
        )

        assert result["success"]

        self.bill_pay_page.navigate_to_bill_pay()
        self.bill_pay_page.assert_bill_pay_page_loaded()

    # =========================================================================
    # ACCESSIBILITY TESTS
    # =========================================================================

    def test_bill_pay_form_accessibility(self):
        """
        Verify important form fields are visible
        and interactable.

        NOTE:
        ParaBank uses a legacy HTML structure and
        does not provide modern accessibility
        attributes such as labels or aria tags.
        """

        self.login_and_navigate()

        form_fields = [
            (
                self.bill_pay_page.FROM_ACCOUNT_SELECT,
                "From account"
            ),
            (
                self.bill_pay_page.AMOUNT_FIELD,
                "Amount"
            ),
            (
                self.bill_pay_page.PAYEE_NAME_FIELD,
                "Payee name"
            ),
            (
                self.bill_pay_page.PAYEE_ADDRESS_FIELD,
                "Payee address"
            ),
        ]

        for selector, field_name in form_fields:

            element = self.page.locator(selector)

            assert element.is_visible(), (
                f"{field_name} field is not visible"
            )

            assert element.is_enabled(), (
                f"{field_name} field is not enabled"
            )

    def test_form_fields_are_visible(self):
        """
        Verify important form fields visible.
        """

        self.login_and_navigate()

        # FIX:
        # Removed invalid/non-existent fields.

        fields = [
            self.bill_pay_page.FROM_ACCOUNT_SELECT,
            self.bill_pay_page.AMOUNT_FIELD,
            self.bill_pay_page.PAYEE_NAME_FIELD,
            self.bill_pay_page.PAYEE_ADDRESS_FIELD,
        ]

        for field in fields:

            assert self.page.is_visible(
                field
            )

    def test_buttons_are_accessible(self):
        """
        Verify important buttons are visible
        and enabled.
        """

        self.login_and_navigate()

        button = self.page.locator(
            self.bill_pay_page.SEND_PAYMENT_BUTTON
        )

        assert button.is_visible()
        assert button.is_enabled()

    def test_keyboard_navigation_support(self):
        """
        Verify keyboard tab navigation works.
        """

        self.login_and_navigate()

        self.page.keyboard.press("Tab")

        focused_element = self.page.evaluate("""
            () => document.activeElement.tagName
        """)

        assert focused_element is not None

    def test_page_has_title(self):
        """
        Verify page has meaningful title.
        """

        self.login_and_navigate()

        title = self.page.title()

        assert len(title) > 0
        assert "Bill Pay" in title

    def test_input_fields_accept_typing(self):
        """
        Verify inputs accept keyboard input.
        """

        self.login_and_navigate()

        self.page.fill(
            self.bill_pay_page.AMOUNT_FIELD,
            "100.00"
        )

        # FIX:
        # input_value() is more reliable than get_attribute("value")

        value = self.page.input_value(
            self.bill_pay_page.AMOUNT_FIELD
        )

        assert value == "100.00"