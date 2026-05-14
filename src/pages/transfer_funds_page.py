"""ParaBank Transfer Funds Page Object Model."""
from typing import Optional, Dict, Any, List
from playwright.sync_api import Page
from src.pages.base_page import BasePage
from src.utils.wait_helpers import WaitHelper, WaitStrategy
from src.utils.assertion_helpers import AssertionHelper
from src.utils.retry_handler import retry_with_backoff
from src.config.logger import log


class TransferFundsPage(BasePage):
    """Enterprise-grade Transfer Funds page object for ParaBank."""

    # Locators
    FROM_ACCOUNT_SELECT = "#fromAccountId"
    TO_ACCOUNT_SELECT = "#toAccountId"
    AMOUNT_FIELD = "#amount"
    DESCRIPTION_FIELD = "#description"
    TRANSFER_BUTTON = "input[type='submit'][value='Transfer']"
    SUCCESS_MESSAGE = "#rightPanel h1"
    ERROR_MESSAGE = ".error"
    TRANSFER_CONFIRMATION = ".confirmation"
    ACCOUNTS_OVERVIEW_LINK = "a[href*='overview.htm']"
    TRANSFER_AMOUNT_DISPLAY = "#amount"
    TRANSFER_FROM_DISPLAY = "#fromAccountId"
    TRANSFER_TO_DISPLAY = "#toAccountId"
    TRANSFER_FORM = "#transferForm"

    def __init__(self, page: Page):
        """Initialize Transfer Funds page with enterprise features."""
        super().__init__(page)
        self.wait_helper = WaitHelper(page)
        self.assert_helper = AssertionHelper(page)
        self.page_url = "parabank/transfer.htm"

    @retry_with_backoff(max_attempts=3, base_delay=0.5)
    def navigate_to_transfer_funds(self) -> None:
        """Navigate to transfer funds page with retry mechanism."""
        base = self.page.url.split('index.htm')[0].split('overview.htm')[0].split('login.htm')[0]
        self.goto(f"{base}transfer.htm")
        self.wait_helper.wait_for_element(self.FROM_ACCOUNT_SELECT, WaitStrategy.ELEMENT_VISIBLE)
        self.wait_helper.wait_for_element(self.TO_ACCOUNT_SELECT, WaitStrategy.ELEMENT_VISIBLE)
        log.info("Successfully navigated to transfer funds page")

    def get_available_accounts(self, select_element: str) -> List[str]:
        """
        Get list of available accounts from dropdown.
        
        Args:
            select_element: CSS selector for select element
            
        Returns:
            List of account IDs
        """
        try:
            self.wait_helper.wait_for_element(select_element, WaitStrategy.ELEMENT_VISIBLE)
            
            # Get all options from select element
            options = self.page.locator(f"{select_element} option")
            account_ids = []
            
            for i in range(options.count()):
                option_text = options.nth(i).text_content()
                if option_text and option_text.strip():
                    account_ids.append(option_text.strip())
            
            log.info(f"Found {len(account_ids)} accounts in {select_element}")
            return account_ids
            
        except Exception as e:
            log.error(f"Failed to get accounts from {select_element}: {e}")
            return []

    def get_from_accounts(self) -> List[str]:
        """Get list of available source accounts."""
        return self.get_available_accounts(self.FROM_ACCOUNT_SELECT)

    def get_to_accounts(self) -> List[str]:
        """Get list of available destination accounts."""
        return self.get_available_accounts(self.TO_ACCOUNT_SELECT)

    def select_from_account(self, account_id: str) -> None:
        """
        Select source account for transfer.
        
        Args:
            account_id: Account ID to select
        """
        try:
            self.wait_helper.wait_for_element(self.FROM_ACCOUNT_SELECT, WaitStrategy.ELEMENT_VISIBLE)
            self.page.select_option(self.FROM_ACCOUNT_SELECT, account_id)
            log.info(f"Selected from account: {account_id}")
        except Exception as e:
            log.error(f"Failed to select from account {account_id}: {e}")
            raise

    def select_to_account(self, account_id: str) -> None:
        """
        Select destination account for transfer.
        
        Args:
            account_id: Account ID to select
        """
        try:
            self.wait_helper.wait_for_element(self.TO_ACCOUNT_SELECT, WaitStrategy.ELEMENT_VISIBLE)
            self.page.select_option(self.TO_ACCOUNT_SELECT, account_id)
            log.info(f"Selected to account: {account_id}")
        except Exception as e:
            log.error(f"Failed to select to account {account_id}: {e}")
            raise

    def enter_amount(self, amount: str) -> None:
        """
        Enter transfer amount.
        
        Args:
            amount: Transfer amount
        """
        self.wait_helper.wait_for_element(self.AMOUNT_FIELD, WaitStrategy.ELEMENT_VISIBLE)
        self.fill(self.AMOUNT_FIELD, amount)
        log.info(f"Entered transfer amount: {amount}")

    def enter_description(self, description: str) -> None:
        """
        Enter transfer description.
        
        Args:
            description: Transfer description
        """
        self.wait_helper.wait_for_element(self.DESCRIPTION_FIELD, WaitStrategy.ELEMENT_VISIBLE)
        self.fill(self.DESCRIPTION_FIELD, description)
        log.info(f"Entered transfer description: {description}")

    def perform_transfer(
        self,
        from_account: str,
        to_account: str,
        amount: str,
        description: Optional[str] = None
    ) -> None:
        """
        Perform complete fund transfer.
        
        Args:
            from_account: Source account ID
            to_account: Destination account ID
            amount: Transfer amount
            description: Optional transfer description
        """
        try:
            self.select_from_account(from_account)
            self.select_to_account(to_account)
            self.enter_amount(amount)
            
            if description:
                self.enter_description(description)
            
            self.click_transfer_button()
            log.info(f"Initiated transfer: {amount} from {from_account} to {to_account}")
            
        except Exception as e:
            log.error(f"Transfer failed: {e}")
            raise

    def click_transfer_button(self) -> None:
        """Click transfer button."""
        self.wait_helper.wait_for_element(self.TRANSFER_BUTTON, WaitStrategy.ELEMENT_CLICKABLE)
        self.click(self.TRANSFER_BUTTON)
        log.info("Clicked transfer button")

    def is_transfer_successful(self) -> bool:
        """Check if transfer was successful."""
        try:
            self.wait_helper.wait_for_element(self.SUCCESS_MESSAGE, WaitStrategy.ELEMENT_VISIBLE, timeout=5000)
            success_text = self.get_text(self.SUCCESS_MESSAGE)
            return "Transfer Complete!" in success_text or "successfully" in success_text.lower()
        except:
            return False

    def get_success_message(self) -> str:
        """Get success message after transfer."""
        try:
            if self.is_visible(self.SUCCESS_MESSAGE, timeout=5000):
                return self.get_text(self.SUCCESS_MESSAGE)
            return ""
        except:
            return ""

    def get_error_message(self) -> str:
        """Get error message from transfer attempt."""
        try:
            if self.is_visible(self.ERROR_MESSAGE, timeout=3000):
                return self.get_text(self.ERROR_MESSAGE)
            return ""
        except:
            return ""

    def get_transfer_confirmation_details(self) -> Dict[str, str]:
        """
        Get transfer confirmation details.
        
        Returns:
            Dictionary with confirmation details
        """
        details = {}
        
        try:
            if self.is_visible(self.TRANSFER_CONFIRMATION, timeout=5000):
                confirmation_text = self.get_text(self.TRANSFER_CONFIRMATION)
                
                # Parse confirmation details (basic parsing)
                lines = confirmation_text.split('\n')
                for line in lines:
                    if 'From:' in line:
                        details['from_account'] = line.split('From:')[1].strip()
                    elif 'To:' in line:
                        details['to_account'] = line.split('To:')[1].strip()
                    elif 'Amount:' in line:
                        details['amount'] = line.split('Amount:')[1].strip()
            
            # Also check individual display elements
            if self.is_visible(self.TRANSFER_FROM_DISPLAY):
                details['from_account'] = self.get_text(self.TRANSFER_FROM_DISPLAY)
            
            if self.is_visible(self.TRANSFER_TO_DISPLAY):
                details['to_account'] = self.get_text(self.TRANSFER_TO_DISPLAY)
            
            if self.is_visible(self.TRANSFER_AMOUNT_DISPLAY):
                details['amount'] = self.get_text(self.TRANSFER_AMOUNT_DISPLAY)
                
        except Exception as e:
            log.error(f"Failed to get transfer confirmation: {e}")
        
        return details

    def validate_transfer_form(self) -> Dict[str, Any]:
        """
        Validate transfer form state and requirements.
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'from_account_selected': False,
            'to_account_selected': False,
            'amount_entered': False,
            'valid_amount': False,
            'different_accounts': False,
            'form_ready': False,
            'issues': []
        }
        
        try:
            # Check from account selection
            from_value = self.get_attribute(self.FROM_ACCOUNT_SELECT, "value")
            validation_results['from_account_selected'] = bool(from_value and from_value.strip())
            
            # Check to account selection
            to_value = self.get_attribute(self.TO_ACCOUNT_SELECT, "value")
            validation_results['to_account_selected'] = bool(to_value and to_value.strip())
            
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
            
            # Check that accounts are different
            if validation_results['from_account_selected'] and validation_results['to_account_selected']:
                validation_results['different_accounts'] = from_value != to_value
                if not validation_results['different_accounts']:
                    validation_results['issues'].append("From and To accounts must be different")
            
            # Overall form readiness
            validation_results['form_ready'] = (
                validation_results['from_account_selected'] and
                validation_results['to_account_selected'] and
                validation_results['amount_entered'] and
                validation_results['valid_amount'] and
                validation_results['different_accounts']
            )
            
        except Exception as e:
            log.error(f"Transfer form validation failed: {e}")
            validation_results['issues'].append(f"Validation error: {str(e)}")
        
        return validation_results

    def clear_transfer_form(self) -> None:
        """Clear all transfer form fields."""
        try:
            # Clear amount field
            self.fill(self.AMOUNT_FIELD, "")
            
            # Clear description field
            self.fill(self.DESCRIPTION_FIELD, "")
            
            log.info("Cleared transfer form")
        except Exception as e:
            log.error(f"Failed to clear transfer form: {e}")

    def click_accounts_overview(self) -> None:
        """Click Accounts Overview link."""
        self.wait_helper.wait_for_and_click(self.ACCOUNTS_OVERVIEW_LINK)
        log.info("Clicked Accounts Overview link")

    def assert_transfer_page_loaded(self) -> None:
        """Assert that transfer funds page is properly loaded."""
        required_elements = [
            self.FROM_ACCOUNT_SELECT,
            self.TO_ACCOUNT_SELECT,
            self.AMOUNT_FIELD,
            self.TRANSFER_BUTTON
        ]
        
        for element in required_elements:
            self.assert_helper.assert_element_visible(element)
        
        self.assert_helper.assert_element_clickable(self.TRANSFER_BUTTON)
        log.info("Transfer funds page loaded successfully")

    def assert_transfer_successful(self, expected_amount: Optional[str] = None) -> None:
        """Assert that transfer was successful."""
        self.assert_helper.assert_element_visible(self.SUCCESS_MESSAGE)
        
        success_text = self.get_text(self.SUCCESS_MESSAGE)
        assert "Transfer Complete!" in success_text or "successfully" in success_text.lower(), \
            "Transfer success message not found"
        
        if expected_amount:
            confirmation_details = self.get_transfer_confirmation_details()
            assert expected_amount in confirmation_details.get('amount', ''), \
                f"Expected amount {expected_amount} not found in confirmation"
        
        log.info("Transfer success assertion verified")

    def assert_transfer_failed(self, expected_error: Optional[str] = None) -> None:
        """Assert that transfer failed with expected error."""
        self.assert_helper.assert_element_visible(self.ERROR_MESSAGE)
        
        if expected_error:
            self.assert_helper.assert_element_contains_text(self.ERROR_MESSAGE, expected_error)
        
        log.info("Transfer failure assertion verified")

    def wait_for_transfer_complete(self, timeout: int = 10000) -> bool:
        """Wait for transfer process to complete."""
        try:
            return self.wait_helper.wait_for_custom_condition(
                condition=lambda: (
                    self.is_visible(self.SUCCESS_MESSAGE, timeout=1000) or 
                    self.is_visible(self.ERROR_MESSAGE, timeout=1000)
                ),
                timeout=timeout,
                message="Transfer completion timeout"
            )
        except:
            return False

    def validate_transfer_limits(self, amount: float) -> Dict[str, Any]:
        """
        Validate transfer against business rules and limits.
        
        Args:
            amount: Transfer amount to validate
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            'within_daily_limit': True,
            'within_transaction_limit': True,
            'sufficient_funds': True,
            'business_hours': True,
            'issues': []
        }
        
        try:
            # Basic transaction limit (example: $10,000 per transaction)
            if amount > 10000:
                validation['within_transaction_limit'] = False
                validation['issues'].append("Amount exceeds single transaction limit of $10,000")
            
            # Basic daily limit (example: $25,000 per day)
            # Note: This would require tracking daily transfers in a real implementation
            if amount > 25000:
                validation['within_daily_limit'] = False
                validation['issues'].append("Amount exceeds daily transfer limit of $25,000")
            
            # Minimum amount check
            if amount <= 0:
                validation['within_transaction_limit'] = False
                validation['issues'].append("Transfer amount must be greater than 0")
            
            # Business hours check (basic implementation)
            current_hour = self.page.evaluate("new Date().getHours()")
            if current_hour < 6 or current_hour > 22:
                validation['business_hours'] = False
                validation['issues'].append("Transfers outside business hours may be delayed")
            
        except Exception as e:
            log.error(f"Transfer limits validation failed: {e}")
            validation['issues'].append(f"Validation error: {str(e)}")
        
        return validation

    def simulate_transfer_with_validation(
        self,
        from_account: str,
        to_account: str,
        amount: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Simulate transfer with comprehensive validation.
        
        Returns:
            Dictionary with simulation results
        """
        result = {
            'success': False,
            'error_message': None,
            'validation_results': None,
            'confirmation_details': None,
            'timestamp': None
        }
        
        try:
            # Validate form before submission
            validation_results = self.validate_transfer_form()
            result['validation_results'] = validation_results
            
            if not validation_results['form_ready']:
                result['error_message'] = "Form validation failed: " + "; ".join(validation_results['issues'])
                return result
            
            # Perform transfer
            self.perform_transfer(from_account, to_account, amount, description)
            
            # Wait for completion
            transfer_complete = self.wait_for_transfer_complete()
            
            if transfer_complete:
                if self.is_transfer_successful():
                    result['success'] = True
                    result['confirmation_details'] = self.get_transfer_confirmation_details()
                    log.info("Transfer simulation successful")
                else:
                    result['error_message'] = self.get_error_message()
                    log.warning(f"Transfer simulation failed: {result['error_message']}")
            
        except Exception as e:
            result['error_message'] = str(e)
            log.error(f"Transfer simulation exception: {e}")
        
        return result
