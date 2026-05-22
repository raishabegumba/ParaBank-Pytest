"""
Security test suite for ParaBank Bill Pay page.

Focused on:
- input validation
- JavaScript handling
- frontend security checks
- malicious input handling
"""

import pytest


@pytest.mark.ui
@pytest.mark.bill_pay
@pytest.mark.security
class TestBillPaySecurity:
    """Security-focused bill pay tests."""

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
        """Login and open Bill Pay page."""

        self.login_page.navigate_to_login()

        result = self.login_page.login_with_validation(
            "john",
            "demo"
        )

        assert result["success"]

        self.bill_pay_page.navigate_to_bill_pay()
        self.bill_pay_page.assert_bill_pay_page_loaded()

    def generate_test_payee_data(self):
        """Generate reusable payee data."""

        return {
            "name": "Security Test Payee",
            "address": "123 Security Street",
            "city": "Security City",
            "state": "TX",
            "zip_code": "75001",
            "phone": "5551234567",
            "account_number": "987654321",
        }

    # =========================================================================
    # SECURITY TESTS
    # =========================================================================

    def test_payment_amount_field_security(self):
        """
        Verify amount field exists and is editable.

        ParaBank does not explicitly define
        input type="text", so avoid strict
        type validation.
        """

        self.login_and_navigate()

        amount_field = self.page.locator(
            self.bill_pay_page.AMOUNT_FIELD
        )

        assert amount_field.is_visible()
        assert amount_field.is_enabled()

        tag_name = amount_field.evaluate(
            "el => el.tagName"
        )

        assert tag_name.lower() == "input"

    def test_bill_pay_form_javascript_functionality(self):
        """
        Verify form accessible through JavaScript.
        """

        self.login_and_navigate()

        form_exists = self.page.evaluate("""
            () => {
                const form = document.querySelector(
                    '#billpayForm'
                );

                return form !== null;
            }
        """)

        assert form_exists

    def test_javascript_form_fill_validation(self):
        """
        Verify JavaScript-based field updates
        correctly populate the form.
        """

        self.login_and_navigate()

        accounts = (
            self.bill_pay_page
            .get_available_accounts()
        )

        assert len(accounts) > 0

        payee_data = (
            self.generate_test_payee_data()
        )

        self.page.evaluate(
            """
            ({ account, payeeName }) => {

                const fromAccount =
                    document.querySelector(
                        "select[name='fromAccountId']"
                    );

                const amount =
                    document.querySelector(
                        "input[name='amount']"
                    );

                const payeeNameField =
                    document.querySelector(
                        "input[name='payee.name']"
                    );

                if (fromAccount) {
                    fromAccount.value = account;
                }

                if (amount) {
                    amount.value = "100.00";
                }

                if (payeeNameField) {
                    payeeNameField.value = payeeName;
                }
            }
            """,
            {
                "account": accounts[0],
                "payeeName": payee_data["name"],
            }
        )

        amount_value = self.page.locator(
            self.bill_pay_page.AMOUNT_FIELD
        ).input_value()

        assert amount_value == "100.00"

    def test_script_injection_in_payee_name(self):
        """
        Verify script injection does not render.
        """

        self.login_and_navigate()

        accounts = (
            self.bill_pay_page
            .get_available_accounts()
        )

        assert len(accounts) > 0

        payee_data = (
            self.generate_test_payee_data()
        )

        malicious_script = (
            "<script>alert('xss')</script>"
        )

        payee_data["name"] = malicious_script

        self.bill_pay_page.send_payment(
            from_account=accounts[0],
            amount="10.00",
            payee_info=payee_data,
        )

        page_content = self.page.content()

        assert malicious_script not in page_content

    def test_html_injection_in_payee_name(self):
        """
        Verify HTML injection does not render.
        """

        self.login_and_navigate()

        accounts = (
            self.bill_pay_page
            .get_available_accounts()
        )

        assert len(accounts) > 0

        payee_data = (
            self.generate_test_payee_data()
        )

        malicious_html = (
            "<b>Injected</b>"
        )

        payee_data["name"] = malicious_html

        self.bill_pay_page.send_payment(
            from_account=accounts[0],
            amount="25.00",
            payee_info=payee_data,
        )

        content = self.page.content()

        assert malicious_html not in content

    def test_sensitive_fields_not_prepopulated(self):
        """
        Verify amount field is empty initially.
        """

        self.login_and_navigate()

        amount_value = (
            self.bill_pay_page.get_attribute(
                self.bill_pay_page.AMOUNT_FIELD,
                "value"
            )
        )

        assert (
            amount_value == ""
            or amount_value is None
        )

    def test_form_does_not_submit_empty_values(self):
        """
        Verify empty form submission fails safely.
        """

        self.login_and_navigate()

        self.bill_pay_page.click_send_payment()

        assert not (
            self.bill_pay_page
            .is_payment_successful()
        )

    def test_invalid_amount_characters_rejected(self):
        """
        Verify invalid amount formats rejected.
        """

        self.login_and_navigate()

        accounts = (
            self.bill_pay_page
            .get_available_accounts()
        )

        assert len(accounts) > 0

        payee_data = (
            self.generate_test_payee_data()
        )

        invalid_amounts = [
            "abc",
            "$$$",
            "10abc",
            "--100",
        ]

        for invalid_amount in invalid_amounts:

            self.bill_pay_page.navigate_to_bill_pay()

            self.bill_pay_page.send_payment(
                from_account=accounts[0],
                amount=invalid_amount,
                payee_info=payee_data,
            )

            assert not (
                self.bill_pay_page
                .is_payment_successful()
            )