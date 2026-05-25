"""ParaBank Loan Request Page Object Model."""

from typing import Optional, Dict, Any, List
from playwright.sync_api import Page

from src.pages.base_page import BasePage
from src.utils.wait_helpers import WaitHelper, WaitStrategy
from src.utils.assertion_helpers import AssertionHelper
from src.utils.retry_handler import retry_with_backoff
from src.config.logger import log
from src.config.settings import get_settings


class LoanRequestPage(BasePage):
    """Enterprise-grade Loan Request page object for ParaBank."""

    # =========================
    # Form Locators
    # =========================
    LOAN_AMOUNT_FIELD = "#requestLoanForm #amount"
    DOWN_PAYMENT_FIELD = "#requestLoanForm #downPayment"
    FROM_ACCOUNT_SELECT = "#requestLoanForm #fromAccountId"

    # Apply button locator can vary by ParaBank build
    APPLY_FOR_LOAN_BUTTON = (
        "input[type='button'][value='Apply Now'], "
        "input[type='submit'][value='Apply Now'], "
        "button:has-text('Apply Now')"
    )

    LOAN_REQUEST_FORM = "#requestLoanForm"

    # =========================
    # Result Section Locators
    # =========================
    LOAN_RESULT_CONTAINER = "#requestLoanResult"

    LOAN_REQUEST_TITLE = "#requestLoanResult h1"

    SUCCESS_MESSAGE = "#loanRequestApproved"
    DENIAL_MESSAGE = "#loanRequestDenied"

    ERROR_MESSAGE = "#loanRequestDenied .error"

    # Stable ParaBank IDs (preferred if available)
    LOAN_STATUS = "#loanStatus"
    LOAN_APPROVAL_MESSAGE = "#loanApprovalMessage"

    ACCOUNTS_OVERVIEW_LINK = "a[href*='overview.htm']"

    def __init__(self, page: Page):
        """Initialize Loan Request page."""
        super().__init__(page)

        self.wait_helper = WaitHelper(page)
        self.assert_helper = AssertionHelper(page)

        self.page_url = "parabank/requestloan.htm"

    # ==========================================================
    # Navigation
    # ==========================================================
    @retry_with_backoff(max_attempts=3, base_delay=0.5)
    def navigate_to_loan_request(self) -> None:
        """Navigate to loan request page."""
        try:
            settings = get_settings()
            self.goto(f"{settings.base_url}/requestloan.htm")
            self.wait_helper.wait_for_element(
            self.LOAN_AMOUNT_FIELD,
            WaitStrategy.ELEMENT_VISIBLE)
            log.info("Successfully navigated to loan request page")
        except Exception as e:
            log.error(
                f"Navigation to Find Transactions page failed: {e}")
            raise

    # ==========================================================
    # Account Handling
    # ==========================================================
    def get_available_accounts(self) -> List[str]:
        """Get list of available accounts."""

        try:
            self.wait_helper.wait_for_element(
                self.FROM_ACCOUNT_SELECT,
                WaitStrategy.ELEMENT_VISIBLE
            )

            options = self.page.locator(
                f"{self.FROM_ACCOUNT_SELECT} option"
            )

            account_ids = []

            for i in range(options.count()):
                option_text = options.nth(i).text_content()

                if option_text and option_text.strip():
                    account_ids.append(option_text.strip())

            log.info(f"Found {len(account_ids)} accounts")

            return account_ids

        except Exception as e:
            log.error(f"Failed to get available accounts: {e}")
            return []

    def select_from_account(self, account_id: str) -> None:
        """Select source account."""

        try:
            self.wait_helper.wait_for_element(
                self.FROM_ACCOUNT_SELECT,
                WaitStrategy.ELEMENT_VISIBLE
            )

            self.page.select_option(
                self.FROM_ACCOUNT_SELECT,
                account_id
            )

            log.info(f"Selected from account: {account_id}")

        except Exception as e:
            log.error(f"Failed to select account {account_id}: {e}")
            raise

    # ==========================================================
    # Form Entry
    # ==========================================================
    def enter_loan_amount(self, amount: str) -> None:
        """Enter loan amount."""

        self.wait_helper.wait_for_element(
            self.LOAN_AMOUNT_FIELD,
            WaitStrategy.ELEMENT_VISIBLE
        )

        self.fill(self.LOAN_AMOUNT_FIELD, amount)

        log.info(f"Entered loan amount: {amount}")

    def enter_down_payment(self, amount: str) -> None:
        """Enter down payment."""

        self.wait_helper.wait_for_element(
            self.DOWN_PAYMENT_FIELD,
            WaitStrategy.ELEMENT_VISIBLE
        )

        self.fill(self.DOWN_PAYMENT_FIELD, amount)

        log.info(f"Entered down payment: {amount}")

    def clear_loan_request_form(self) -> None:
        """Clear all form fields."""

        try:
            self.fill(self.LOAN_AMOUNT_FIELD, "")
            self.fill(self.DOWN_PAYMENT_FIELD, "")

            log.info("Cleared loan request form")

        except Exception as e:
            log.error(f"Failed to clear loan request form: {e}")

    # ==========================================================
    # Actions
    # ==========================================================
    def click_apply_for_loan(self) -> None:
        """Click apply for loan."""

        self.wait_helper.wait_for_element(
            self.APPLY_FOR_LOAN_BUTTON,
            WaitStrategy.ELEMENT_CLICKABLE
        )

        self.click(self.APPLY_FOR_LOAN_BUTTON)

        log.info("Clicked apply for loan button")

    def apply_for_loan(
        self,
        loan_amount: str,
        down_payment: str,
        from_account: str
    ) -> None:
        """
        Apply for loan.

        Args:
            loan_amount: Requested loan amount
            down_payment: Down payment amount
            from_account: Source account
        """

        try:
            self.select_from_account(from_account)

            self.enter_loan_amount(loan_amount)

            self.enter_down_payment(down_payment)

            validation_results = self.validate_loan_request_form()

            if not validation_results["form_ready"]:
                raise ValueError(
                    "Loan request form validation failed: "
                    + "; ".join(validation_results["issues"])
                )

            self.click_apply_for_loan()

            log.info(
                f"Applied for loan: {loan_amount}, "
                f"down payment: {down_payment}"
            )

        except Exception as e:
            log.error(f"Loan application failed: {e}")
            raise

    # ==========================================================
    # Result Parsing
    # ==========================================================
    def wait_for_loan_processing_complete(
        self,
        timeout: int = 10000
    ) -> bool:
        """Wait for loan processing result."""

        try:
            return self.wait_helper.wait_for_custom_condition(
                condition=lambda: (
                    self.is_visible(
                        self.SUCCESS_MESSAGE,
                        timeout=1000
                    )
                    or
                    self.is_visible(
                        self.DENIAL_MESSAGE,
                        timeout=1000
                    )
                ),
                timeout=timeout,
                message="Loan processing completion timeout"
            )

        except Exception:
            return False

    def _extract_table_value(self, label: str) -> str:
        """
        Extract value from result table.

        Example:
            Loan Provider: -> Wealth Securities Dynamic Loans
        """

        try:
            row = (
                self.page.locator(
                    "#requestLoanResult tr"
                )
                .filter(has_text=label)
            )

            if row.count() == 0:
                return ""

            cells = row.locator("td")

            if cells.count() < 2:
                return ""

            value = cells.nth(1).text_content()

            return value.strip() if value else ""

        except Exception as e:
            log.debug(f"Failed extracting table value [{label}]: {e}")
            return ""

    def get_loan_result_details(self) -> Dict[str, Any]:
        """Get structured loan result details."""

        details = {
            "title": "",
            "provider": "",
            "date": "",
            "status": "",
            "message": "",
            "approved": False,
            "denied": False
        }

        try:
            self.wait_helper.wait_for_element(
                self.LOAN_RESULT_CONTAINER,
                WaitStrategy.ELEMENT_VISIBLE,
                timeout=10000
            )

            if self.is_visible(self.LOAN_REQUEST_TITLE):
                details["title"] = self.get_text(
                    self.LOAN_REQUEST_TITLE
                )

            details["provider"] = self._extract_table_value(
                "Loan Provider:"
            )

            details["date"] = self._extract_table_value(
                "Date:"
            )

            details["status"] = self._extract_table_value(
                "Status:"
            )

            # Denied message
            if self.is_visible(self.ERROR_MESSAGE, timeout=2000):
                details["message"] = self.get_text(
                    self.ERROR_MESSAGE
                )

            # Approval message
            elif self.is_visible(
                self.LOAN_APPROVAL_MESSAGE,
                timeout=2000
            ):
                details["message"] = self.get_text(
                    self.LOAN_APPROVAL_MESSAGE
                )

            status = details["status"].strip().lower()

            details["approved"] = status == "approved"
            details["denied"] = status == "denied"

            log.info(f"Loan result details: {details}")

        except Exception as e:
            log.error(f"Failed to get loan result details: {e}")

        return details

    def get_loan_confirmation_details(self) -> Dict[str, Any]:
        """Backward-compatible wrapper."""

        return self.get_loan_result_details()

    def get_success_message(self) -> str:
        """Get approval message."""

        try:
            details = self.get_loan_result_details()

            if details["approved"]:
                return details["message"]

            return ""

        except Exception:
            return ""

    def get_error_message(self) -> str:
        """Get denial message."""

        try:
            details = self.get_loan_result_details()

            if details["denied"]:
                return details["message"]

            return ""

        except Exception:
            return ""

    def is_loan_approved(self) -> bool:
        """Check if loan approved."""

        try:
            details = self.get_loan_result_details()
            return details["approved"]

        except Exception:
            return False

    def is_loan_denied(self) -> bool:
        """Check if loan denied."""

        try:
            details = self.get_loan_result_details()
            return details["denied"]

        except Exception:
            return False

    # ==========================================================
    # Validation
    # ==========================================================
    def validate_loan_request_form(self) -> Dict[str, Any]:
        """Validate form state."""

        validation_results = {
            "from_account_selected": False,
            "loan_amount_entered": False,
            "valid_loan_amount": False,
            "down_payment_entered": False,
            "valid_down_payment": False,
            "form_ready": False,
            "issues": []
        }

        try:
            from_value = self.get_input_value(
                self.FROM_ACCOUNT_SELECT)

            validation_results["from_account_selected"] = bool(
                from_value and from_value.strip()
            )

            loan_amount_value = self.get_input_value(
                self.LOAN_AMOUNT_FIELD                
            )

            validation_results["loan_amount_entered"] = bool(
                loan_amount_value and loan_amount_value.strip()
            )

            if validation_results["loan_amount_entered"]:

                try:
                    loan_amount_float = float(
                        loan_amount_value
                        .replace("$", "")
                        .replace(",", "")
                    )

                    validation_results["valid_loan_amount"] = (
                        loan_amount_float > 0
                    )

                    if loan_amount_float <= 0:
                        validation_results["issues"].append(
                            "Loan amount must be greater than 0"
                        )

                except ValueError:
                    validation_results["issues"].append(
                        "Invalid loan amount format"
                    )

            down_payment_value = self.get_input_value(
                self.DOWN_PAYMENT_FIELD              
            )

            validation_results["down_payment_entered"] = bool(
                down_payment_value and down_payment_value.strip()
            )

            if validation_results["down_payment_entered"]:

                try:
                    down_payment_float = float(
                        down_payment_value
                        .replace("$", "")
                        .replace(",", "")
                    )

                    validation_results["valid_down_payment"] = (
                        down_payment_float >= 0
                    )

                    if down_payment_float < 0:
                        validation_results["issues"].append(
                            "Down payment cannot be negative"
                        )

                except ValueError:
                    validation_results["issues"].append(
                        "Invalid down payment format"
                    )

            validation_results["form_ready"] = (
                validation_results["from_account_selected"]
                and
                validation_results["loan_amount_entered"]
                and
                validation_results["valid_loan_amount"]
                and
                validation_results["down_payment_entered"]
                and
                validation_results["valid_down_payment"]
            )

        except Exception as e:
            log.error(f"Form validation failed: {e}")

            validation_results["issues"].append(str(e))

        return validation_results

    def validate_loan_eligibility(
        self,
        loan_amount: float,
        down_payment: float
    ) -> Dict[str, Any]:
        """
        Validate loan eligibility based on business rules.
 
        Rules enforced:
          - Minimum loan amount: $1,000
          - Maximum loan amount: $100,000
          - Minimum down payment: 10% of loan amount
          - Maximum LTV: 90%  (down_payment / loan_amount >= 0.10)
 
        Returns a dict with granular flags so tests can assert
        on individual rule outcomes.
        """
        MIN_LOAN   = 1_000.0
        MAX_LOAN   = 100_000.0
        MIN_DOWN_PCT = 0.10   # 10%
        MAX_LTV      = 0.90   # 90%
 
        results: Dict[str, Any] = {
            "eligible":               False,
            "within_loan_range":      False,
            "adequate_down_payment":  False,
            "reasonable_loan_to_value": False,
            "issues":                 [],
        }
 
        try:
            # Range check
            results["within_loan_range"] = MIN_LOAN <= loan_amount <= MAX_LOAN
            if not results["within_loan_range"]:
                results["issues"].append(
                    f"Loan amount ${loan_amount} outside allowed range "
                    f"${MIN_LOAN}–${MAX_LOAN}"
                )
 
            # Down payment percentage check
            if loan_amount > 0:
                down_pct = down_payment / loan_amount
                results["adequate_down_payment"] = down_pct >= MIN_DOWN_PCT
                if not results["adequate_down_payment"]:
                    results["issues"].append(
                        f"Down payment {down_pct*100:.1f}% is below "
                        f"the required {MIN_DOWN_PCT*100:.0f}%"
                    )
 
                # LTV check (mirrors down payment rule for a standard mortgage)
                ltv = 1 - (down_payment / loan_amount)
                results["reasonable_loan_to_value"] = ltv <= MAX_LTV
                if not results["reasonable_loan_to_value"]:
                    results["issues"].append(
                        f"LTV {ltv*100:.1f}% exceeds maximum {MAX_LTV*100:.0f}%"
                    )
            else:
                results["issues"].append("Loan amount must be greater than 0")
 
            results["eligible"] = (
                results["within_loan_range"]
                and results["adequate_down_payment"]
                and results["reasonable_loan_to_value"]
            )
 
        except Exception as e:
            log.error(f"Eligibility validation error: {e}")
            results["issues"].append(str(e))
 
        log.debug(f"Eligibility results: {results}")
        return results
 
    def simulate_loan_request_with_validation(
        self,
        loan_amount: str,
        down_payment: str,
        from_account: str,
    ) -> Dict[str, Any]:
        """
        Run a full loan request with pre-flight validation and eligibility
        checks, then return a structured result dictionary.
 
        Returns:
            {
                "success": bool,          # True if processing completed
                "approved": bool,         # True if loan was approved
                "validation_results": {}, # Output of validate_loan_request_form()
                "eligibility_results": {},# Output of validate_loan_eligibility()
                "confirmation_details": {},# Populated on approval
                "error": str,             # Set on exception
            }
        """
        result: Dict[str, Any] = {
            "success":              False,
            "approved":             False,
            "validation_results":   {},
            "eligibility_results":  {},
            "confirmation_details": {},
            "error":                "",
        }
 
        try:
            # Pre-fill form so validate_loan_request_form() can inspect values
            self.select_from_account(from_account)
            self.enter_loan_amount(loan_amount)
            self.enter_down_payment(down_payment)
 
            result["validation_results"] = self.validate_loan_request_form()
 
            # Eligibility check (numeric)
            try:
                loan_float = float(
                    loan_amount.replace("$", "").replace(",", "")
                )
                down_float = float(
                    down_payment.replace("$", "").replace(",", "")
                )
                result["eligibility_results"] = self.validate_loan_eligibility(
                    loan_float, down_float
                )
            except ValueError as e:
                result["eligibility_results"] = {"eligible": False, "issues": [str(e)]}
 
            if not result["validation_results"].get("form_ready"):
                result["error"] = (
                    "Form validation failed: "
                    + "; ".join(result["validation_results"].get("issues", []))
                )
                return result
 
            self.click_apply_for_loan()
            processing_complete = self.wait_for_loan_processing_complete()
 
            if processing_complete:
                result["success"] = True
                result["approved"] = self.is_loan_approved()
 
                if result["approved"]:
                    result["confirmation_details"] = (
                        self.get_loan_confirmation_details()
                    )
 
            log.info(f"Simulation result: {result}")
 
        except Exception as e:
            result["error"] = str(e)
            log.error(f"Loan simulation failed: {e}")
 
        return result
    # ==========================================================
    # Assertions
    # ==========================================================
    def assert_loan_request_page_loaded(self) -> None:
        """Assert page loaded."""

        required_elements = [
            self.LOAN_AMOUNT_FIELD,
            self.DOWN_PAYMENT_FIELD,
            self.FROM_ACCOUNT_SELECT,
            self.APPLY_FOR_LOAN_BUTTON
        ]

        for element in required_elements:
            self.assert_helper.assert_element_visible(element)

        self.assert_helper.assert_element_is_clickable(
            self.APPLY_FOR_LOAN_BUTTON
        )

        log.info("Loan request page loaded successfully")

    def assert_loan_approved(self) -> None:
        """Assert approved result."""

        details = self.get_loan_result_details()

        assert details["approved"], (
            f"Expected approved loan but got: "
            f"{details['status']}"
        )

        log.info("Loan approval assertion verified")

    def assert_loan_denied(
        self,
        expected_error: Optional[str] = None
    ) -> None:
        """Assert denied result."""

        details = self.get_loan_result_details()

        assert details["denied"], (
            f"Expected denied loan but got: "
            f"{details['status']}"
        )

        if expected_error:
            assert expected_error.lower() in (
                details["message"].lower()
            ), (
                f"Expected error message "
                f"'{expected_error}' not found in "
                f"'{details['message']}'"
            )

        log.info("Loan denial assertion verified")

    # ==========================================================
    # Navigation Links
    # ==========================================================
    def click_accounts_overview(self) -> None:
        """Click Accounts Overview."""

        self.wait_helper.wait_for_and_click(
            self.ACCOUNTS_OVERVIEW_LINK
        )

        log.info("Clicked Accounts Overview link")