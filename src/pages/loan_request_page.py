"""ParaBank Loan Request Page Object Model."""
from typing import Optional, Dict, Any, List
from playwright.sync_api import Page
from src.pages.base_page import BasePage
from src.utils.wait_helpers import WaitHelper, WaitStrategy
from src.utils.assertion_helpers import AssertionHelper
from src.utils.retry_handler import retry_with_backoff
from src.config.logger import log


class LoanRequestPage(BasePage):
    """Enterprise-grade Loan Request page object for ParaBank."""

    # Locators
    LOAN_AMOUNT_FIELD = "#amount"
    DOWN_PAYMENT_FIELD = "#downPayment"
    FROM_ACCOUNT_SELECT = "#fromAccountId"
    # Apply button locator can vary by ParaBank build (value spacing, input/button).
    APPLY_FOR_LOAN_BUTTON = "input[type='submit'][value='Apply Now'], input[type='submit'][value='Apply Now '], input[type='submit'][name='apply'], input[type='submit'], button:has-text('Apply Now')"
    SUCCESS_MESSAGE = "#rightPanel h1"
    ERROR_MESSAGE = ".error"
    LOAN_CONFIRMATION = ".loanConfirmation"
    LOAN_RESULT_MESSAGE = "#loanResult"
    LOAN_STATUS = "#loanStatus"
    LOAN_APPROVAL_MESSAGE = "#loanApprovalMessage"
    ACCOUNTS_OVERVIEW_LINK = "a[href*='overview.htm']"
    LOAN_REQUEST_FORM = "#loanForm"

    def __init__(self, page: Page):
        """Initialize Loan Request page with enterprise features."""
        super().__init__(page)
        self.wait_helper = WaitHelper(page)
        self.assert_helper = AssertionHelper(page)
        self.page_url = "parabank/requestloan.htm"

    @retry_with_backoff(max_attempts=3, base_delay=0.5)
    def navigate_to_loan_request(self) -> None:
        """Navigate to loan request page with retry mechanism."""
        # Navigate using current page URL prefix (Playwright Browser object doesn't expose internal base_url options reliably).
        base = self.page.url.split('index.htm')[0].split('overview.htm')[0].split('login.htm')[0]
        self.goto(f"{base}requestloan.htm")
        self.wait_helper.wait_for_element(self.LOAN_AMOUNT_FIELD, WaitStrategy.ELEMENT_VISIBLE)
        log.info("Successfully navigated to loan request page")

    def get_available_accounts(self) -> List[str]:
        """Get list of available accounts for loan funding."""
        try:
            self.wait_helper.wait_for_element(self.FROM_ACCOUNT_SELECT, WaitStrategy.ELEMENT_VISIBLE)
            
            options = self.page.locator(f"{self.FROM_ACCOUNT_SELECT} option")
            account_ids = []
            
            for i in range(options.count()):
                option_text = options.nth(i).text_content()
                if option_text and option_text.strip():
                    account_ids.append(option_text.strip())
            
            log.info(f"Found {len(account_ids)} accounts for loan request")
            return account_ids
            
        except Exception as e:
            log.error(f"Failed to get available accounts: {e}")
            return []

    def select_from_account(self, account_id: str) -> None:
        """Select source account for loan."""
        try:
            self.wait_helper.wait_for_element(self.FROM_ACCOUNT_SELECT, WaitStrategy.ELEMENT_VISIBLE)
            self.page.select_option(self.FROM_ACCOUNT_SELECT, account_id)
            log.info(f"Selected from account: {account_id}")
        except Exception as e:
            log.error(f"Failed to select from account {account_id}: {e}")
            raise

    def enter_loan_amount(self, amount: str) -> None:
        """Enter loan amount."""
        self.wait_helper.wait_for_element(self.LOAN_AMOUNT_FIELD, WaitStrategy.ELEMENT_VISIBLE)
        self.fill(self.LOAN_AMOUNT_FIELD, amount)
        log.info(f"Entered loan amount: {amount}")

    def enter_down_payment(self, amount: str) -> None:
        """Enter down payment amount."""
        self.wait_helper.wait_for_element(self.DOWN_PAYMENT_FIELD, WaitStrategy.ELEMENT_VISIBLE)
        self.fill(self.DOWN_PAYMENT_FIELD, amount)
        log.info(f"Entered down payment: {amount}")

    def apply_for_loan(
        self,
        loan_amount: str,
        down_payment: str,
        from_account: str
    ) -> None:
        """
        Apply for loan with all required information.
        
        Args:
            loan_amount: Requested loan amount
            down_payment: Down payment amount
            from_account: Account for loan processing
        """
        try:
            self.select_from_account(from_account)
            self.enter_loan_amount(loan_amount)
            self.enter_down_payment(down_payment)
            self.click_apply_for_loan()
            log.info(f"Applied for loan: {loan_amount} with down payment {down_payment}")
        except Exception as e:
            log.error(f"Loan application failed: {e}")
            raise

    def click_apply_for_loan(self) -> None:
        """Click apply for loan button."""
        self.wait_helper.wait_for_element(self.APPLY_FOR_LOAN_BUTTON, WaitStrategy.ELEMENT_CLICKABLE)
        self.click(self.APPLY_FOR_LOAN_BUTTON)
        log.info("Clicked apply for loan button")

    def is_loan_approved(self) -> bool:
        """Check if loan was approved."""
        try:
            self.wait_helper.wait_for_element(self.SUCCESS_MESSAGE, WaitStrategy.ELEMENT_VISIBLE, timeout=5000)
            success_text = self.get_text(self.SUCCESS_MESSAGE)
            return "Loan Request Processed" in success_text or "approved" in success_text.lower()
        except:
            return False

    def is_loan_denied(self) -> bool:
        """Check if loan was denied."""
        try:
            if self.is_visible(self.ERROR_MESSAGE, timeout=5000):
                error_text = self.get_text(self.ERROR_MESSAGE)
                return "denied" in error_text.lower() or "rejected" in error_text.lower()
            return False
        except:
            return False

    def get_success_message(self) -> str:
        """Get success message after loan application."""
        try:
            if self.is_visible(self.SUCCESS_MESSAGE, timeout=5000):
                return self.get_text(self.SUCCESS_MESSAGE)
            return ""
        except:
            return ""

    def get_error_message(self) -> str:
        """Get error message from loan application."""
        try:
            if self.is_visible(self.ERROR_MESSAGE, timeout=3000):
                return self.get_text(self.ERROR_MESSAGE)
            return ""
        except:
            return ""

    def get_loan_confirmation_details(self) -> Dict[str, str]:
        """Get loan confirmation details."""
        details = {}
        
        try:
            if self.is_visible(self.LOAN_CONFIRMATION, timeout=5000):
                confirmation_text = self.get_text(self.LOAN_CONFIRMATION)
                
                # Parse confirmation details
                lines = confirmation_text.split('\n')
                for line in lines:
                    if 'Loan Amount:' in line:
                        details['loan_amount'] = line.split('Loan Amount:')[1].strip()
                    elif 'Down Payment:' in line:
                        details['down_payment'] = line.split('Down Payment:')[1].strip()
                    elif 'From Account:' in line:
                        details['from_account'] = line.split('From Account:')[1].strip()
            
            # Check individual display elements
            if self.is_visible(self.LOAN_RESULT_MESSAGE):
                details['result_message'] = self.get_text(self.LOAN_RESULT_MESSAGE)
            
            if self.is_visible(self.LOAN_STATUS):
                details['loan_status'] = self.get_text(self.LOAN_STATUS)
            
            if self.is_visible(self.LOAN_APPROVAL_MESSAGE):
                details['approval_message'] = self.get_text(self.LOAN_APPROVAL_MESSAGE)
                
        except Exception as e:
            log.error(f"Failed to get loan confirmation: {e}")
        
        return details

    def validate_loan_request_form(self) -> Dict[str, Any]:
        """Validate loan request form state and requirements."""
        validation_results = {
            'from_account_selected': False,
            'loan_amount_entered': False,
            'valid_loan_amount': False,
            'down_payment_entered': False,
            'valid_down_payment': False,
            'form_ready': False,
            'issues': []
        }
        
        try:
            # Check from account selection
            from_value = self.get_attribute(self.FROM_ACCOUNT_SELECT, "value")
            validation_results['from_account_selected'] = bool(from_value and from_value.strip())
            
            # Check loan amount entry
            loan_amount_value = self.get_attribute(self.LOAN_AMOUNT_FIELD, "value")
            validation_results['loan_amount_entered'] = bool(loan_amount_value and loan_amount_value.strip())
            
            # Validate loan amount format
            if validation_results['loan_amount_entered']:
                try:
                    loan_amount_float = float(loan_amount_value.replace('$', '').replace(',', ''))
                    validation_results['valid_loan_amount'] = loan_amount_float > 0
                    if loan_amount_float <= 0:
                        validation_results['issues'].append("Loan amount must be greater than 0")
                except ValueError:
                    validation_results['valid_loan_amount'] = False
                    validation_results['issues'].append("Invalid loan amount format")
            
            # Check down payment entry
            down_payment_value = self.get_attribute(self.DOWN_PAYMENT_FIELD, "value")
            validation_results['down_payment_entered'] = bool(down_payment_value and down_payment_value.strip())
            
            # Validate down payment format
            if validation_results['down_payment_entered']:
                try:
                    down_payment_float = float(down_payment_value.replace('$', '').replace(',', ''))
                    validation_results['valid_down_payment'] = down_payment_float >= 0
                    if down_payment_float < 0:
                        validation_results['issues'].append("Down payment cannot be negative")
                except ValueError:
                    validation_results['valid_down_payment'] = False
                    validation_results['issues'].append("Invalid down payment format")
            
            # Overall form readiness
            validation_results['form_ready'] = (
                validation_results['from_account_selected'] and
                validation_results['loan_amount_entered'] and
                validation_results['valid_loan_amount'] and
                validation_results['down_payment_entered'] and
                validation_results['valid_down_payment']
            )
            
        except Exception as e:
            log.error(f"Loan request form validation failed: {e}")
            validation_results['issues'].append(f"Validation error: {str(e)}")
        
        return validation_results

    def clear_loan_request_form(self) -> None:
        """Clear all loan request form fields."""
        try:
            self.fill(self.LOAN_AMOUNT_FIELD, "")
            self.fill(self.DOWN_PAYMENT_FIELD, "")
            log.info("Cleared loan request form")
        except Exception as e:
            log.error(f"Failed to clear loan request form: {e}")

    def click_accounts_overview(self) -> None:
        """Click Accounts Overview link."""
        self.wait_helper.wait_for_and_click(self.ACCOUNTS_OVERVIEW_LINK)
        log.info("Clicked Accounts Overview link")

    def assert_loan_request_page_loaded(self) -> None:
        """Assert that loan request page is properly loaded."""
        required_elements = [
            self.LOAN_AMOUNT_FIELD,
            self.DOWN_PAYMENT_FIELD,
            self.FROM_ACCOUNT_SELECT,
            self.APPLY_FOR_LOAN_BUTTON
        ]
        
        for element in required_elements:
            self.assert_helper.assert_element_visible(element)
        
        self.assert_helper.assert_element_clickable(self.APPLY_FOR_LOAN_BUTTON)
        log.info("Loan request page loaded successfully")

    def assert_loan_approved(self) -> None:
        """Assert that loan was approved."""
        self.assert_helper.assert_element_visible(self.SUCCESS_MESSAGE)
        
        success_text = self.get_text(self.SUCCESS_MESSAGE)
        assert "Loan Request Processed" in success_text or "approved" in success_text.lower(), \
            "Loan approval message not found"
        
        log.info("Loan approval assertion verified")

    def assert_loan_denied(self, expected_error: Optional[str] = None) -> None:
        """Assert that loan was denied."""
        self.assert_helper.assert_element_visible(self.ERROR_MESSAGE)
        
        error_text = self.get_text(self.ERROR_MESSAGE)
        assert "denied" in error_text.lower() or "rejected" in error_text.lower(), \
            "Loan denial message not found"
        
        if expected_error:
            self.assert_helper.assert_element_contains_text(self.ERROR_MESSAGE, expected_error)
        
        log.info("Loan denial assertion verified")

    def wait_for_loan_processing_complete(self, timeout: int = 10000) -> bool:
        """Wait for loan processing to complete."""
        try:
            return self.wait_helper.wait_for_custom_condition(
                condition=lambda: (
                    self.is_visible(self.SUCCESS_MESSAGE, timeout=1000) or 
                    self.is_visible(self.ERROR_MESSAGE, timeout=1000)
                ),
                timeout=timeout,
                message="Loan processing completion timeout"
            )
        except:
            return False

    def validate_loan_eligibility(self, loan_amount: float, down_payment: float) -> Dict[str, Any]:
        """Validate loan eligibility against business rules."""
        validation = {
            'within_loan_limits': True,
            'adequate_down_payment': True,
            'reasonable_loan_to_value': True,
            'eligible': True,
            'issues': []
        }
        
        try:
            # Loan amount limits (example: $1,000 - $100,000)
            if loan_amount < 1000:
                validation['within_loan_limits'] = False
                validation['issues'].append("Loan amount below minimum of $1,000")
            elif loan_amount > 100000:
                validation['within_loan_limits'] = False
                validation['issues'].append("Loan amount exceeds maximum of $100,000")
            
            # Down payment requirements (example: minimum 10%)
            if loan_amount > 0:
                down_payment_percentage = (down_payment / loan_amount) * 100
                if down_payment_percentage < 10:
                    validation['adequate_down_payment'] = False
                    validation['issues'].append("Down payment must be at least 10% of loan amount")
            
            # Loan-to-value ratio (example: maximum 90%)
            if loan_amount > 0:
                loan_to_value = ((loan_amount - down_payment) / loan_amount) * 100
                if loan_to_value > 90:
                    validation['reasonable_loan_to_value'] = False
                    validation['issues'].append("Loan-to-value ratio exceeds 90%")
            
            # Overall eligibility
            validation['eligible'] = (
                validation['within_loan_limits'] and
                validation['adequate_down_payment'] and
                validation['reasonable_loan_to_value']
            )
            
        except Exception as e:
            log.error(f"Loan eligibility validation failed: {e}")
            validation['issues'].append(f"Validation error: {str(e)}")
        
        return validation

    def simulate_loan_request_with_validation(
        self,
        loan_amount: str,
        down_payment: str,
        from_account: str
    ) -> Dict[str, Any]:
        """Simulate loan request with comprehensive validation."""
        result = {
            'success': False,
            'approved': False,
            'error_message': None,
            'validation_results': None,
            'eligibility_results': None,
            'confirmation_details': None,
            'timestamp': None
        }
        
        try:
            # Validate form before submission
            validation_results = self.validate_loan_request_form()
            result['validation_results'] = validation_results
            
            if not validation_results['form_ready']:
                result['error_message'] = "Form validation failed: " + "; ".join(validation_results['issues'])
                return result
            
            # Validate eligibility
            loan_amount_float = float(loan_amount.replace('$', '').replace(',', ''))
            down_payment_float = float(down_payment.replace('$', '').replace(',', ''))
            
            eligibility_results = self.validate_loan_eligibility(loan_amount_float, down_payment_float)
            result['eligibility_results'] = eligibility_results
            
            if not eligibility_results['eligible']:
                result['error_message'] = "Loan eligibility check failed: " + "; ".join(eligibility_results['issues'])
                return result
            
            # Perform loan application
            self.apply_for_loan(loan_amount, down_payment, from_account)
            
            # Wait for completion
            processing_complete = self.wait_for_loan_processing_complete()
            
            if processing_complete:
                if self.is_loan_approved():
                    result['success'] = True
                    result['approved'] = True
                    result['confirmation_details'] = self.get_loan_confirmation_details()
                    log.info("Loan request simulation successful - approved")
                elif self.is_loan_denied():
                    result['success'] = True
                    result['approved'] = False
                    result['error_message'] = self.get_error_message()
                    log.info("Loan request simulation successful - denied")
                else:
                    result['error_message'] = "Unknown loan processing result"
                    log.warning("Loan request simulation - unknown result")
            
        except Exception as e:
            result['error_message'] = str(e)
            log.error(f"Loan request simulation exception: {e}")
        
        return result
