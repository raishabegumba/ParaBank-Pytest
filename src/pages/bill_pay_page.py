"""ParaBank Bill Pay Page Object Model."""
from typing import Optional, Dict, Any, List
from playwright.sync_api import Page
from src.pages.base_page import BasePage
from src.utils.wait_helpers import WaitHelper, WaitStrategy
from src.utils.assertion_helpers import AssertionHelper
from src.utils.retry_handler import retry_with_backoff
from src.config.logger import log


class BillPayPage(BasePage):
    """Enterprise-grade Bill Pay page object for ParaBank."""

    # Locators
    PAYEE_NAME_FIELD = "#billpayForm input[name='payee.name']"
    PAYEE_ADDRESS_FIELD = "#billpayForm input[name='payee.address.street']"
    PAYEE_CITY_FIELD = "#billpayForm input[name='payee.address.city']"
    PAYEE_STATE_FIELD = "#billpayForm input[name='payee.address.state']"
    PAYEE_ZIP_FIELD = "#billpayForm input[name='payee.address.zipCode']"
    PAYEE_PHONE_FIELD = "#billpayForm input[name='payee.phoneNumber']"
    PAYEE_ACCOUNT_FIELD = "#billpayForm input[name='payee.accountNumber']"
    PAYEE_VERIFY_ACCOUNT_FIELD = "#billpayForm input[name='verifyAccount']"
    FROM_ACCOUNT_SELECT = "#billpayForm select[name='fromAccountId']"
    AMOUNT_FIELD = "#billpayForm input[name='amount']"
    # ParaBank Angular renders the submit as <button type="submit">, not
    # <input type="submit">.  The :is() pseudo-class covers both variants
    # so the locator works regardless of the template version in use.
    SEND_PAYMENT_BUTTON = "input[type='button'][value='Send Payment']"
    SUCCESS_TITLE = "#billpayResult h1"
    SUCCESS_MESSAGE = "#billpayResult p"
    ERROR_MESSAGE = "#billpayError p"
    PAYMENT_CONFIRMATION = ".ng-scope table"
    ACCOUNTS_OVERVIEW_LINK = "a[href*='overview.htm']"
    BILL_PAY_FORM = "#billpayForm"

    def __init__(self, page: Page):
        """Initialize Bill Pay page with enterprise features."""
        super().__init__(page)
        self.wait_helper = WaitHelper(page)
        self.assert_helper = AssertionHelper(page)
        self.page_url = "parabank/billpay.htm"

    # =========================================================================
    # NAVIGATION
    # =========================================================================

    @retry_with_backoff(max_attempts=3, base_delay=0.5)
    def navigate_to_bill_pay(self) -> None:
        """Navigate safely to bill pay page."""
        try:
            base_url = self.page.url.split("/parabank")[0]
            url = f"{base_url}/parabank/billpay.htm"

            self.goto(url)

            # Wait for the form itself — FROM_ACCOUNT_SELECT may not be
            # populated immediately, so we anchor on the form container.
            self.wait_helper.wait_for_element(
                self.BILL_PAY_FORM,
                WaitStrategy.ELEMENT_VISIBLE,
                timeout=15000,
            )

            log.info("Successfully navigated to bill pay page")

        except Exception as e:
            log.error(f"Navigation failed: {e}")
            raise

    # =========================================================================
    # ACCOUNT HELPERS
    # =========================================================================

    def get_available_accounts(self) -> List[str]:
        """Return visible text labels of every option in the from-account dropdown."""
        try:
            self.wait_helper.wait_for_element(
                self.FROM_ACCOUNT_SELECT,
                WaitStrategy.ELEMENT_VISIBLE,
            )

            options = self.page.locator(f"{self.FROM_ACCOUNT_SELECT} option")
            account_ids: List[str] = []

            for i in range(options.count()):
                text = options.nth(i).text_content()
                if text and text.strip():
                    account_ids.append(text.strip())

            log.info(f"Found {len(account_ids)} accounts")
            return account_ids

        except Exception as e:
            log.error(f"Failed to get accounts: {e}")
            return []

    def select_from_account(self, account_id: str) -> None:
        """Select source account by its visible label."""
        try:
            self.wait_helper.wait_for_element(
                self.FROM_ACCOUNT_SELECT,
                WaitStrategy.ELEMENT_VISIBLE,
            )

            self.page.select_option(self.FROM_ACCOUNT_SELECT, label=account_id)
            log.info(f"Selected from account: {account_id}")

        except Exception as e:
            log.error(f"Failed to select account {account_id}: {e}")
            raise

    # =========================================================================
    # FORM FIELD HELPERS
    # =========================================================================

    def fill_payee_information(
        self,
        name: str,
        address: str,
        city: str,
        state: str,
        zip_code: str,
        phone: str,
        account_number: str,
        verify_account_number: Optional[str] = None,
    ) -> None:
        """Fill all payee information fields."""
        try:
            self.wait_helper.wait_for_element(
                self.PAYEE_NAME_FIELD, WaitStrategy.ELEMENT_VISIBLE
            )

            self.fill(self.PAYEE_NAME_FIELD, name)
            self.fill(self.PAYEE_ADDRESS_FIELD, address)
            self.fill(self.PAYEE_CITY_FIELD, city)
            self.fill(self.PAYEE_STATE_FIELD, state)
            self.fill(self.PAYEE_ZIP_FIELD, zip_code)
            self.fill(self.PAYEE_PHONE_FIELD, phone)
            self.fill(self.PAYEE_ACCOUNT_FIELD, account_number)

            # Fill verify-account field when present
            verify_value = verify_account_number or account_number
            if self.is_visible(self.PAYEE_VERIFY_ACCOUNT_FIELD, timeout=2000):
                self.fill(self.PAYEE_VERIFY_ACCOUNT_FIELD, verify_value)

            log.info(f"Filled payee information for: {name}")

        except Exception as e:
            log.error(f"Failed to fill payee information: {e}")
            raise

    def enter_payment_amount(self, amount: str) -> None:
        """Enter the payment amount."""
        self.wait_helper.wait_for_element(
            self.AMOUNT_FIELD, WaitStrategy.ELEMENT_VISIBLE
        )
        self.fill(self.AMOUNT_FIELD, amount)
        log.info(f"Entered payment amount: {amount}")

    # =========================================================================
    # HIGH-LEVEL ACTION
    # =========================================================================

    def send_payment(
        self,
        from_account: str,
        amount: str,
        payee_info: Optional[Dict[str, str]] = None,
        # The parameters below are accepted for API compatibility with the
        # test suite but are not used by the real ParaBank bill-pay form,
        # which has no dedicated date or description fields.
        date: Optional[str] = None,           # noqa: ignored — not on form
        description: Optional[str] = None,    # noqa: ignored — not on form
        add_new_payee: Optional[bool] = None,  # noqa: ignored — not on form
    ) -> None:
        """
        Orchestrate a complete bill-payment submission.

        Parameters
        ----------
        from_account : str
            Visible label of the source account (e.g. "12345").
        amount : str
            Payment amount as a string (e.g. "100.00").
        payee_info : dict, optional
            Keyword arguments forwarded to fill_payee_information().
        date : str, optional
            Accepted for test-suite compatibility; not present on the form.
        description : str, optional
            Accepted for test-suite compatibility; not present on the form.
        add_new_payee : bool, optional
            Accepted for test-suite compatibility; not present on the form.
        """
        try:
            if payee_info:
                self.fill_payee_information(**payee_info)

            self.select_from_account(from_account)
            self.enter_payment_amount(amount)
            self.click_send_payment()

            log.info(f"Initiated payment: {amount} from {from_account}")

        except Exception as e:
            log.error(f"Payment failed: {e}")
            raise

    def click_send_payment(self) -> None:
        """Click the Send Payment submit button."""
        self.wait_helper.wait_for_element(
            self.SEND_PAYMENT_BUTTON, WaitStrategy.ELEMENT_CLICKABLE
        )
        self.click(self.SEND_PAYMENT_BUTTON)
        log.info("Clicked send payment button")

    # =========================================================================
    # RESULT INSPECTION
    # =========================================================================

    def is_payment_successful(self) -> bool:
        """Return True if the payment-success heading is visible."""
        try:
            self.wait_helper.wait_for_element(
                self.SUCCESS_TITLE, WaitStrategy.ELEMENT_VISIBLE, timeout=5000
            )
            success_text = self.get_text(self.SUCCESS_TITLE)
            return (
                "Bill Payment Complete" in success_text
                or "successfully" in success_text.lower()
            )
        except Exception:
            return False

    def get_success_message(self) -> str:
        """Return the success heading text, or an empty string."""
        try:
            if self.is_visible(self.SUCCESS_TITLE, timeout=5000):
                return self.get_text(self.SUCCESS_TITLE)
            return ""
        except Exception:
            return ""

    def get_error_message(self) -> str:
        """Return the first visible error message text, or an empty string."""
        try:
            if self.is_visible(self.ERROR_MESSAGE, timeout=3000):
                return self.get_text(self.ERROR_MESSAGE)
            return ""
        except Exception:
            return ""

    def get_payment_confirmation_details(self) -> Dict[str, str]:
        """Parse and return key/value pairs from the confirmation block."""
        details: Dict[str, str] = {}
        try:
            if self.is_visible(self.PAYMENT_CONFIRMATION, timeout=5000):
                confirmation_text = self.get_text(self.PAYMENT_CONFIRMATION)
                for line in confirmation_text.split("\n"):
                    if "From:" in line:
                        details["from_account"] = line.split("From:")[1].strip()
                    elif "To:" in line:
                        details["payee"] = line.split("To:")[1].strip()
                    elif "Amount:" in line:
                        details["amount"] = line.split("Amount:")[1].strip()
        except Exception as e:
            log.error(f"Failed to get payment confirmation: {e}")
        return details

    def wait_for_payment_complete(self, timeout: int = 10000) -> bool:
        """Block until either a success or error indicator appears."""
        try:
            return self.wait_helper.wait_for_custom_condition(
                condition=lambda: (
                    self.is_visible(self.SUCCESS_TITLE, timeout=1000)
                    or self.is_visible(self.ERROR_MESSAGE, timeout=1000)
                ),
                timeout=timeout,
                message="Payment completion timeout",
            )
        except Exception:
            return False

    # =========================================================================
    # VALIDATION HELPERS
    # =========================================================================
    def _input_value(self, selector: str) -> str:
        """Read the live value of an input/select element.
        Playwright's input_value() reads the actual current field value instead.
        """
        try:
            return self.page.locator(selector).input_value() or ""
        except Exception:
            return ""
        
    def validate_payment_form(self) -> Dict[str, Any]:
        """
        Inspect current field values and return a validation summary.

        Keys
        ----
        from_account_selected, amount_entered, valid_amount,
        payee_info_complete, form_ready, issues
        """
        results: Dict[str, Any] = {
            "from_account_selected": False,
            "amount_entered": False,
            "valid_amount": False,
            "payee_info_complete": False,
            "form_ready": False,
            "issues": [],
        }

        try:
            # From-account
            from_value = self._input_value(self.FROM_ACCOUNT_SELECT)
            results["from_account_selected"] = bool(
                from_value and from_value.strip()
            )
            if not results["from_account_selected"]:
                results["issues"].append("From account not selected")

            # Amount presence
            amount_value = self._input_value(self.AMOUNT_FIELD)
            results["amount_entered"] = bool(amount_value and amount_value.strip())
            if not results["amount_entered"]:
                results["issues"].append("Payment amount is required")

            # Amount value
            if results["amount_entered"]:
                try:
                    amount_float = float(
                        amount_value.replace("$", "").replace(",", "")
                    )
                    results["valid_amount"] = amount_float > 0
                    if not results["valid_amount"]:
                        results["issues"].append("Amount must be greater than 0")
                except ValueError:
                    results["valid_amount"] = False
                    results["issues"].append("Invalid amount format")

            # Payee fields
            payee_name = self._input_value(self.PAYEE_NAME_FIELD)
            payee_address = self._input_value(self.PAYEE_ADDRESS_FIELD)
            results["payee_info_complete"] = bool(
                payee_name
                and payee_name.strip()
                and payee_address
                and payee_address.strip()
            )
            if not results["payee_info_complete"]:
                results["issues"].append("Payee information incomplete")

            results["form_ready"] = (
                results["from_account_selected"]
                and results["amount_entered"]
                and results["valid_amount"]
                and results["payee_info_complete"]
            )

        except Exception as e:
            log.error(f"Payment form validation failed: {e}")
            results["issues"].append(f"Validation error: {str(e)}")

        return results

    def validate_payment_limits(self, amount: float) -> Dict[str, Any]:
        """Check amount against business-rule thresholds."""
        validation: Dict[str, Any] = {
            "within_daily_limit": True,
            "within_transaction_limit": True,
            "sufficient_funds": True,
            "business_hours": True,
            "issues": [],
        }

        try:
            if amount <= 0:
                validation["within_transaction_limit"] = False
                validation["issues"].append("Payment amount must be greater than 0")

            elif amount > 5000:
                validation["within_transaction_limit"] = False
                validation["issues"].append(
                    "Amount exceeds single payment limit of $5,000"
                )

            if amount > 15000:
                validation["within_daily_limit"] = False
                validation["issues"].append(
                    "Amount exceeds daily payment limit of $15,000"
                )

            current_hour = self.page.evaluate("new Date().getHours()")
            if current_hour < 6 or current_hour > 22:
                validation["business_hours"] = False
                validation["issues"].append(
                    "Payments outside business hours may be delayed"
                )

        except Exception as e:
            log.error(f"Payment limits validation failed: {e}")
            validation["issues"].append(f"Validation error: {str(e)}")

        return validation

    def clear_payment_form(self) -> None:
        """Clear every editable text field on the payment form."""
        fields_to_clear = [
            self.PAYEE_NAME_FIELD,
            self.PAYEE_ADDRESS_FIELD,
            self.PAYEE_CITY_FIELD,
            self.PAYEE_STATE_FIELD,
            self.PAYEE_ZIP_FIELD,
            self.PAYEE_PHONE_FIELD,
            self.PAYEE_ACCOUNT_FIELD,
            self.AMOUNT_FIELD,
        ]
        try:
            for field in fields_to_clear:
                self.fill(field, "")
            log.info("Cleared payment form")
        except Exception as e:
            log.error(f"Failed to clear payment form: {e}")

    # =========================================================================
    # ASSERTIONS
    # =========================================================================

    def assert_bill_pay_page_loaded(self) -> None:
        """Assert all key form elements are visible."""
        required = [
            self.BILL_PAY_FORM,
            self.FROM_ACCOUNT_SELECT,
            self.AMOUNT_FIELD,
            self.SEND_PAYMENT_BUTTON,
        ]
        for element in required:
            self.assert_helper.assert_element_visible(element)
        log.info("Bill pay page loaded successfully")

    def assert_payment_successful(
        self, expected_amount: Optional[str] = None
    ) -> None:
        """Assert the payment success heading is visible and correct."""
        self.assert_helper.assert_element_visible(self.SUCCESS_TITLE)

        success_text = self.get_text(self.SUCCESS_TITLE)
        assert (
            "Bill Payment Complete" in success_text
            or "successfully" in success_text.lower()
        ), "Payment success message not found"

        if expected_amount:
            confirmation_details = self.get_payment_confirmation_details()
            assert expected_amount in confirmation_details.get("amount", ""), (
                f"Expected amount {expected_amount} not found in confirmation"
            )

        log.info("Payment success assertion verified")

    def assert_payment_failed(
        self, expected_error: Optional[str] = None
    ) -> None:
        """Assert that an error message is visible after a failed payment."""
        self.assert_helper.assert_element_visible(self.ERROR_MESSAGE)

        if expected_error:
            self.assert_helper.assert_element_contains_text(
                self.ERROR_MESSAGE, expected_error
            )

        log.info("Payment failure assertion verified")

    # =========================================================================
    # NAVIGATION
    # =========================================================================

    def click_accounts_overview(self) -> None:
        """Click the Accounts Overview navigation link."""
        self.wait_helper.wait_for_and_click(self.ACCOUNTS_OVERVIEW_LINK)
        log.info("Clicked Accounts Overview link")