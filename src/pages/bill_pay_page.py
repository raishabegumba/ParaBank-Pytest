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
    PAYEE_NAME_FIELD = "#payee.name"
    PAYEE_ADDRESS_FIELD = "#payee.address.street"
    PAYEE_CITY_FIELD = "#payee.address.city"
    PAYEE_STATE_FIELD = "#payee.address.state"
    PAYEE_ZIP_FIELD = "#payee.address.zipCode"
    PAYEE_PHONE_FIELD = "#payee.phoneNumber"
    PAYEE_ACCOUNT_FIELD = "#payee.accountNumber"
    FROM_ACCOUNT_SELECT = "#fromAccountId"
    AMOUNT_FIELD = "#amount"
    PAYMENT_DATE_FIELD = "#paymentDate"
    DESCRIPTION_FIELD = "#description"
    SEND_PAYMENT_BUTTON = "input[type='submit'][value='Send Payment']"
    SUCCESS_MESSAGE = "#rightPanel h1"
    ERROR_MESSAGE = ".error"
    PAYMENT_CONFIRMATION = ".confirmation"
    ACCOUNTS_OVERVIEW_LINK = "a[href*='overview.htm']"
    ADD_NEW_PAYEE_CHECKBOX = "#addNewPayee"
    PAYEE_LIST_SELECT = "#payeeId"
    BILL_PAY_FORM = "#billpayForm"

    def __init__(self, page: Page):
        """Initialize Bill Pay page with enterprise features."""
        super().__init__(page)
        self.wait_helper = WaitHelper(page)
        self.assert_helper = AssertionHelper(page)
        self.page_url = "parabank/billpay.htm"

    @retry_with_backoff(max_attempts=3, base_delay=0.5)
    def navigate_to_bill_pay(self) -> None:
        """Navigate to bill pay page with retry mechanism."""
        base = self.page.url.split('index.htm')[0].split('overview.htm')[0].split('login.htm')[0]
        self.goto(f"{base}billpay.htm")
        self.wait_helper.wait_for_element(self.FROM_ACCOUNT_SELECT, WaitStrategy.ELEMENT_VISIBLE)
        log.info("Successfully navigated to bill pay page")

    def get_available_accounts(self) -> List[str]:
        """Get list of available accounts for payment."""
        try:
            self.wait_helper.wait_for_element(self.FROM_ACCOUNT_SELECT, WaitStrategy.ELEMENT_VISIBLE)
            
            options = self.page.locator(f"{self.FROM_ACCOUNT_SELECT} option")
            account_ids = []
            
            for i in range(options.count()):
                option_text = options.nth(i).text_content()
                if option_text and option_text.strip():
                    account_ids.append(option_text.strip())
            
            log.info(f"Found {len(account_ids)} accounts for bill payment")
            return account_ids
            
        except Exception as e:
            log.error(f"Failed to get available accounts: {e}")
            return []

    def select_from_account(self, account_id: str) -> None:
        """Select source account for payment."""
        try:
            self.wait_helper.wait_for_element(self.FROM_ACCOUNT_SELECT, WaitStrategy.ELEMENT_VISIBLE)
            self.page.select_option(self.FROM_ACCOUNT_SELECT, account_id)
            log.info(f"Selected from account: {account_id}")
        except Exception as e:
            log.error(f"Failed to select from account {account_id}: {e}")
            raise

    def fill_payee_information(
        self,
        name: str,
        address: str,
        city: str,
        state: str,
        zip_code: str,
        phone: str,
        account_number: str
    ) -> None:
        """Fill payee information fields."""
        try:
            self.wait_helper.wait_for_element(self.PAYEE_NAME_FIELD, WaitStrategy.ELEMENT_VISIBLE)
            
            self.fill(self.PAYEE_NAME_FIELD, name)
            self.fill(self.PAYEE_ADDRESS_FIELD, address)
            self.fill(self.PAYEE_CITY_FIELD, city)
            self.fill(self.PAYEE_STATE_FIELD, state)
            self.fill(self.PAYEE_ZIP_FIELD, zip_code)
            self.fill(self.PAYEE_PHONE_FIELD, phone)
            self.fill(self.PAYEE_ACCOUNT_FIELD, account_number)
            
            log.info(f"Filled payee information for: {name}")
        except Exception as e:
            log.error(f"Failed to fill payee information: {e}")
            raise

    def enter_payment_amount(self, amount: str) -> None:
        """Enter payment amount."""
        self.wait_helper.wait_for_element(self.AMOUNT_FIELD, WaitStrategy.ELEMENT_VISIBLE)
        self.fill(self.AMOUNT_FIELD, amount)
        log.info(f"Entered payment amount: {amount}")

    def enter_payment_date(self, date: str) -> None:
        """Enter payment date."""
        self.wait_helper.wait_for_element(self.PAYMENT_DATE_FIELD, WaitStrategy.ELEMENT_VISIBLE)
        self.fill(self.PAYMENT_DATE_FIELD, date)
        log.info(f"Entered payment date: {date}")

    def enter_description(self, description: str) -> None:
        """Enter payment description."""
        self.wait_helper.wait_for_element(self.DESCRIPTION_FIELD, WaitStrategy.ELEMENT_VISIBLE)
        self.fill(self.DESCRIPTION_FIELD, description)
        log.info(f"Entered payment description: {description}")

    def add_new_payee(self, add_new: bool = True) -> None:
        """Check/uncheck add new payee checkbox."""
        try:
            if add_new:
                self.check(self.ADD_NEW_PAYEE_CHECKBOX)
                log.info("Checked add new payee")
            else:
                self.uncheck(self.ADD_NEW_PAYEE_CHECKBOX)
                log.info("Unchecked add new payee")
        except Exception as e:
            log.error(f"Failed to set add new payee: {e}")

    def select_existing_payee(self, payee_id: str) -> None:
        """Select existing payee from dropdown."""
        try:
            self.wait_helper.wait_for_element(self.PAYEE_LIST_SELECT, WaitStrategy.ELEMENT_VISIBLE)
            self.page.select_option(self.PAYEE_LIST_SELECT, payee_id)
            log.info(f"Selected existing payee: {payee_id}")
        except Exception as e:
            log.error(f"Failed to select existing payee {payee_id}: {e}")
            raise

    def send_payment(
        self,
        from_account: str,
        amount: str,
        date: str,
        description: Optional[str] = None,
        payee_info: Optional[Dict[str, str]] = None,
        add_new_payee: bool = True
    ) -> None:
        """
        Send payment with all required information.
        
        Args:
            from_account: Source account ID
            amount: Payment amount
            date: Payment date
            description: Optional description
            payee_info: Payee information dict (for new payees)
            add_new_payee: Whether to add as new payee
        """
        try:
            self.select_from_account(from_account)
            self.enter_payment_amount(amount)
            self.enter_payment_date(date)
            
            if description:
                self.enter_description(description)
            
            if payee_info and add_new_payee:
                self.add_new_payee(True)
                self.fill_payee_information(**payee_info)
            
            self.click_send_payment()
            log.info(f"Initiated payment: {amount} from {from_account}")
            
        except Exception as e:
            log.error(f"Payment failed: {e}")
            raise

    def click_send_payment(self) -> None:
        """Click send payment button."""
        self.wait_helper.wait_for_element(self.SEND_PAYMENT_BUTTON, WaitStrategy.ELEMENT_CLICKABLE)
        self.click(self.SEND_PAYMENT_BUTTON)
        log.info("Clicked send payment button")

    def is_payment_successful(self) -> bool:
        """Check if payment was successful."""
        try:
            self.wait_helper.wait_for_element(self.SUCCESS_MESSAGE, WaitStrategy.ELEMENT_VISIBLE, timeout=5000)
            success_text = self.get_text(self.SUCCESS_MESSAGE)
            return "Bill Payment Complete" in success_text or "successfully" in success_text.lower()
        except:
            return False

    def get_success_message(self) -> str:
        """Get success message after payment."""
        try:
            if self.is_visible(self.SUCCESS_MESSAGE, timeout=5000):
                return self.get_text(self.SUCCESS_MESSAGE)
            return ""
        except:
            return ""

    def get_error_message(self) -> str:
        """Get error message from payment attempt."""
        try:
            if self.is_visible(self.ERROR_MESSAGE, timeout=3000):
                return self.get_text(self.ERROR_MESSAGE)
            return ""
        except:
            return ""

    def get_payment_confirmation_details(self) -> Dict[str, str]:
        """Get payment confirmation details."""
        details = {}
        
        try:
            if self.is_visible(self.PAYMENT_CONFIRMATION, timeout=5000):
                confirmation_text = self.get_text(self.PAYMENT_CONFIRMATION)
                
                # Parse confirmation details
                lines = confirmation_text.split('\n')
                for line in lines:
                    if 'From:' in line:
                        details['from_account'] = line.split('From:')[1].strip()
                    elif 'To:' in line:
                        details['payee'] = line.split('To:')[1].strip()
                    elif 'Amount:' in line:
                        details['amount'] = line.split('Amount:')[1].strip()
                    elif 'Date:' in line:
                        details['date'] = line.split('Date:')[1].strip()
                        
        except Exception as e:
            log.error(f"Failed to get payment confirmation: {e}")
        
        return details

    def validate_payment_form(self) -> Dict[str, Any]:
        """Validate payment form state and requirements."""
        validation_results = {
            'from_account_selected': False,
            'amount_entered': False,
            'valid_amount': False,
            'date_entered': False,
            'valid_date': False,
            'payee_info_complete': False,
            'form_ready': False,
            'issues': []
        }
        
        try:
            # Check from account selection
            from_value = self.get_attribute(self.FROM_ACCOUNT_SELECT, "value")
            validation_results['from_account_selected'] = bool(from_value and from_value.strip())
            
            # Check amount entry
            amount_value = self.get_attribute(self.AMOUNT_FIELD, "value")
            validation_results['amount_entered'] = bool(amount_value and amount_value.strip())
            
            # Validate amount format
            if validation_results['amount_entered']:
                try:
                    amount_float = float(amount_value.replace('$', '').replace(',', ''))
                    validation_results['valid_amount'] = amount_float > 0
                    if amount_float <= 0:
                        validation_results['issues'].append("Amount must be greater than 0")
                except ValueError:
                    validation_results['valid_amount'] = False
                    validation_results['issues'].append("Invalid amount format")
            
            # Check date entry
            date_value = self.get_attribute(self.PAYMENT_DATE_FIELD, "value")
            validation_results['date_entered'] = bool(date_value and date_value.strip())
            
            # Basic date validation
            if validation_results['date_entered']:
                # This is basic validation - could be enhanced with proper date parsing
                validation_results['valid_date'] = len(date_value) >= 6  # Basic MM/DD/YY check
            
            # Check payee information if adding new payee
            is_add_new_checked = self.is_checked(self.ADD_NEW_PAYEE_CHECKBOX)
            if is_add_new_checked:
                payee_name = self.get_attribute(self.PAYEE_NAME_FIELD, "value")
                payee_address = self.get_attribute(self.PAYEE_ADDRESS_FIELD, "value")
                validation_results['payee_info_complete'] = bool(
                    payee_name and payee_name.strip() and
                    payee_address and payee_address.strip()
                )
                if not validation_results['payee_info_complete']:
                    validation_results['issues'].append("Payee information incomplete")
            else:
                validation_results['payee_info_complete'] = True
            
            # Overall form readiness
            validation_results['form_ready'] = (
                validation_results['from_account_selected'] and
                validation_results['amount_entered'] and
                validation_results['valid_amount'] and
                validation_results['date_entered'] and
                validation_results['valid_date'] and
                validation_results['payee_info_complete']
            )
            
        except Exception as e:
            log.error(f"Payment form validation failed: {e}")
            validation_results['issues'].append(f"Validation error: {str(e)}")
        
        return validation_results

    def clear_payment_form(self) -> None:
        """Clear all payment form fields."""
        try:
            fields_to_clear = [
                self.PAYEE_NAME_FIELD,
                self.PAYEE_ADDRESS_FIELD,
                self.PAYEE_CITY_FIELD,
                self.PAYEE_STATE_FIELD,
                self.PAYEE_ZIP_FIELD,
                self.PAYEE_PHONE_FIELD,
                self.PAYEE_ACCOUNT_FIELD,
                self.AMOUNT_FIELD,
                self.PAYMENT_DATE_FIELD,
                self.DESCRIPTION_FIELD
            ]
            
            for field in fields_to_clear:
                self.fill(field, "")
            
            log.info("Cleared payment form")
        except Exception as e:
            log.error(f"Failed to clear payment form: {e}")

    def click_accounts_overview(self) -> None:
        """Click Accounts Overview link."""
        self.wait_helper.wait_for_and_click(self.ACCOUNTS_OVERVIEW_LINK)
        log.info("Clicked Accounts Overview link")

    def assert_bill_pay_page_loaded(self) -> None:
        """Assert that bill pay page is properly loaded."""
        required_elements = [
            self.FROM_ACCOUNT_SELECT,
            self.AMOUNT_FIELD,
            self.PAYMENT_DATE_FIELD,
            self.SEND_PAYMENT_BUTTON
        ]
        
        for element in required_elements:
            self.assert_helper.assert_element_visible(element)
        
        self.assert_helper.assert_element_clickable(self.SEND_PAYMENT_BUTTON)
        log.info("Bill pay page loaded successfully")

    def assert_payment_successful(self, expected_amount: Optional[str] = None) -> None:
        """Assert that payment was successful."""
        self.assert_helper.assert_element_visible(self.SUCCESS_MESSAGE)
        
        success_text = self.get_text(self.SUCCESS_MESSAGE)
        assert "Bill Payment Complete" in success_text or "successfully" in success_text.lower(), \
            "Payment success message not found"
        
        if expected_amount:
            confirmation_details = self.get_payment_confirmation_details()
            assert expected_amount in confirmation_details.get('amount', ''), \
                f"Expected amount {expected_amount} not found in confirmation"
        
        log.info("Payment success assertion verified")

    def assert_payment_failed(self, expected_error: Optional[str] = None) -> None:
        """Assert that payment failed with expected error."""
        self.assert_helper.assert_element_visible(self.ERROR_MESSAGE)
        
        if expected_error:
            self.assert_helper.assert_element_contains_text(self.ERROR_MESSAGE, expected_error)
        
        log.info("Payment failure assertion verified")

    def wait_for_payment_complete(self, timeout: int = 10000) -> bool:
        """Wait for payment process to complete."""
        try:
            return self.wait_helper.wait_for_custom_condition(
                condition=lambda: (
                    self.is_visible(self.SUCCESS_MESSAGE, timeout=1000) or 
                    self.is_visible(self.ERROR_MESSAGE, timeout=1000)
                ),
                timeout=timeout,
                message="Payment completion timeout"
            )
        except:
            return False

    def validate_payment_limits(self, amount: float) -> Dict[str, Any]:
        """Validate payment against business rules and limits."""
        validation = {
            'within_daily_limit': True,
            'within_transaction_limit': True,
            'sufficient_funds': True,
            'business_hours': True,
            'future_date_allowed': True,
            'issues': []
        }
        
        try:
            # Transaction limit (example: $5,000 per payment)
            if amount > 5000:
                validation['within_transaction_limit'] = False
                validation['issues'].append("Amount exceeds single payment limit of $5,000")
            
            # Daily limit (example: $15,000 per day)
            if amount > 15000:
                validation['within_daily_limit'] = False
                validation['issues'].append("Amount exceeds daily payment limit of $15,000")
            
            # Minimum amount check
            if amount <= 0:
                validation['within_transaction_limit'] = False
                validation['issues'].append("Payment amount must be greater than 0")
            
            # Business hours check
            current_hour = self.page.evaluate("new Date().getHours()")
            if current_hour < 6 or current_hour > 22:
                validation['business_hours'] = False
                validation['issues'].append("Payments outside business hours may be delayed")
            
        except Exception as e:
            log.error(f"Payment limits validation failed: {e}")
            validation['issues'].append(f"Validation error: {str(e)}")
        
        return validation
