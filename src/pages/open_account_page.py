"""ParaBank Open Account Page Object Model."""
from typing import Optional, Dict, Any, List
from playwright.sync_api import Page
from src.pages.base_page import BasePage
from src.utils.wait_helpers import WaitHelper, WaitStrategy
from src.utils.assertion_helpers import AssertionHelper
from src.utils.retry_handler import retry_with_backoff
from src.config.logger import log


class OpenAccountPage(BasePage):
    """Enterprise-grade Open Account page object for ParaBank."""

    # Locators
    ACCOUNT_TYPE_SELECT = "#type"
    FROM_ACCOUNT_SELECT = "#fromAccountId"
    # Some ParaBank builds render the submit button as input[value] and others as a button/input without exact value.
    OPEN_NEW_ACCOUNT_BUTTON = "input[type='submit'][value='Open New Account'], input[type='submit'][value='Open New Account '], input[type='submit'][name='open'], input[type='submit'], button:has-text('Open New Account')"
    SUCCESS_MESSAGE = "#rightPanel h1"
    ERROR_MESSAGE = ".error"
    ACCOUNT_DETAILS = ".accountDetails"
    NEW_ACCOUNT_ID = "#newAccountId"
    ACCOUNT_TYPE_DISPLAY = "#accountType"
    ACCOUNT_BALANCE = "#balance"
    ACCOUNTS_OVERVIEW_LINK = "a[href*='overview.htm']"
    OPEN_ACCOUNT_FORM = "#openAccountForm"

    def __init__(self, page: Page):
        """Initialize Open Account page with enterprise features."""
        super().__init__(page)
        self.wait_helper = WaitHelper(page)
        self.assert_helper = AssertionHelper(page)
        self.page_url = "parabank/openaccount.htm"

    @retry_with_backoff(max_attempts=3, base_delay=0.5)
    def navigate_to_open_account(self) -> None:
        """Navigate to open account page with retry mechanism."""
        # Navigate using the page's current base URL / configured test URL.
        # Playwright's Browser object does not reliably expose internal browser options.
        # ParaBank is typically served from the same host as the current page.
        # Use the current URL's prefix to navigate reliably.
        base = self.page.url.split('index.htm')[0].split('overview.htm')[0].split('login.htm')[0]
        self.goto(f"{base}openaccount.htm")
        # Ensure the open account form is fully loaded before assertions
        self.wait_helper.wait_for_element(self.ACCOUNT_TYPE_SELECT, WaitStrategy.ELEMENT_VISIBLE, timeout=20000)
        self.wait_helper.wait_for_element(self.FROM_ACCOUNT_SELECT, WaitStrategy.ELEMENT_VISIBLE, timeout=20000)
        self.wait_helper.wait_for_element(self.ACCOUNT_TYPE_SELECT, WaitStrategy.ELEMENT_VISIBLE)
        self.wait_helper.wait_for_element(self.FROM_ACCOUNT_SELECT, WaitStrategy.ELEMENT_VISIBLE)
        log.info("Successfully navigated to open account page")

    def get_account_types(self) -> List[str]:
        """Get list of available account types."""
        try:
            self.wait_helper.wait_for_element(self.ACCOUNT_TYPE_SELECT, WaitStrategy.ELEMENT_VISIBLE)
            
            options = self.page.locator(f"{self.ACCOUNT_TYPE_SELECT} option")
            account_types = []
            
            for i in range(options.count()):
                option_text = options.nth(i).text_content()
                if option_text and option_text.strip():
                    account_types.append(option_text.strip())
            
            log.info(f"Found {len(account_types)} account types")
            return account_types
            
        except Exception as e:
            log.error(f"Failed to get account types: {e}")
            return []

    def get_source_accounts(self) -> List[str]:
        """Get list of available source accounts."""
        try:
            self.wait_helper.wait_for_element(self.FROM_ACCOUNT_SELECT, WaitStrategy.ELEMENT_VISIBLE)
            
            options = self.page.locator(f"{self.FROM_ACCOUNT_SELECT} option")
            account_ids = []
            
            for i in range(options.count()):
                option_text = options.nth(i).text_content()
                if option_text and option_text.strip():
                    account_ids.append(option_text.strip())
            
            log.info(f"Found {len(account_ids)} source accounts")
            return account_ids
            
        except Exception as e:
            log.error(f"Failed to get source accounts: {e}")
            return []

    def select_account_type(self, account_type: str) -> None:
        """Select account type to open."""
        try:
            self.wait_helper.wait_for_element(self.ACCOUNT_TYPE_SELECT, WaitStrategy.ELEMENT_VISIBLE)
            self.page.select_option(self.ACCOUNT_TYPE_SELECT, account_type)
            log.info(f"Selected account type: {account_type}")
        except Exception as e:
            log.error(f"Failed to select account type {account_type}: {e}")
            raise

    def select_source_account(self, account_id: str) -> None:
        """Select source account for funding."""
        try:
            self.wait_helper.wait_for_element(self.FROM_ACCOUNT_SELECT, WaitStrategy.ELEMENT_VISIBLE)
            self.page.select_option(self.FROM_ACCOUNT_SELECT, account_id)
            log.info(f"Selected source account: {account_id}")
        except Exception as e:
            log.error(f"Failed to select source account {account_id}: {e}")
            raise

    def open_new_account(self, account_type: str, source_account: str) -> None:
        """
        Open new account with specified type and funding source.
        
        Args:
            account_type: Type of account to open
            source_account: Account to fund from
        """
        try:
            self.select_account_type(account_type)
            self.select_source_account(source_account)
            self.click_open_new_account()
            log.info(f"Initiated opening {account_type} account funded by {source_account}")
        except Exception as e:
            log.error(f"Open account failed: {e}")
            raise

    def click_open_new_account(self) -> None:
        """Click open new account button."""
        self.wait_helper.wait_for_element(self.OPEN_NEW_ACCOUNT_BUTTON, WaitStrategy.ELEMENT_CLICKABLE)
        self.click(self.OPEN_NEW_ACCOUNT_BUTTON)
        log.info("Clicked open new account button")

    def is_account_opened_successfully(self) -> bool:
        """Check if account was opened successfully."""
        try:
            self.wait_helper.wait_for_element(self.SUCCESS_MESSAGE, WaitStrategy.ELEMENT_VISIBLE, timeout=5000)
            success_text = self.get_text(self.SUCCESS_MESSAGE)
            return "Account Opened!" in success_text or "successfully" in success_text.lower()
        except:
            return False

    def get_success_message(self) -> str:
        """Get success message after opening account."""
        try:
            if self.is_visible(self.SUCCESS_MESSAGE, timeout=5000):
                return self.get_text(self.SUCCESS_MESSAGE)
            return ""
        except:
            return ""

    def get_error_message(self) -> str:
        """Get error message from account opening attempt."""
        try:
            if self.is_visible(self.ERROR_MESSAGE, timeout=3000):
                return self.get_text(self.ERROR_MESSAGE)
            return ""
        except:
            return ""

    def get_new_account_details(self) -> Dict[str, str]:
        """Get details of the newly opened account."""
        details = {}
        
        try:
            if self.is_visible(self.ACCOUNT_DETAILS, timeout=5000):
                # Get account ID
                if self.is_visible(self.NEW_ACCOUNT_ID):
                    details['account_id'] = self.get_text(self.NEW_ACCOUNT_ID)
                
                # Get account type
                if self.is_visible(self.ACCOUNT_TYPE_DISPLAY):
                    details['account_type'] = self.get_text(self.ACCOUNT_TYPE_DISPLAY)
                
                # Get account balance
                if self.is_visible(self.ACCOUNT_BALANCE):
                    details['balance'] = self.get_text(self.ACCOUNT_BALANCE)
                
                log.info(f"Retrieved new account details: {details}")
                
        except Exception as e:
            log.error(f"Failed to get new account details: {e}")
        
        return details

    def get_new_account_id(self) -> str:
        """Get the ID of the newly opened account."""
        try:
            if self.is_visible(self.NEW_ACCOUNT_ID, timeout=5000):
                return self.get_text(self.NEW_ACCOUNT_ID).strip()
            return ""
        except:
            return ""

    def validate_open_account_form(self) -> Dict[str, Any]:
        """Validate open account form state and requirements."""
        validation_results = {
            'account_type_selected': False,
            'source_account_selected': False,
            'different_accounts': True,  # Always true for new account
            'form_ready': False,
            'issues': []
        }
        
        try:
            # Check account type selection
            account_type_value = self.get_attribute(self.ACCOUNT_TYPE_SELECT, "value")
            validation_results['account_type_selected'] = bool(account_type_value and account_type_value.strip())
            
            # Check source account selection
            source_account_value = self.get_attribute(self.FROM_ACCOUNT_SELECT, "value")
            validation_results['source_account_selected'] = bool(source_account_value and source_account_value.strip())
            
            # Overall form readiness
            validation_results['form_ready'] = (
                validation_results['account_type_selected'] and
                validation_results['source_account_selected']
            )
            
            if not validation_results['account_type_selected']:
                validation_results['issues'].append("Account type must be selected")
            
            if not validation_results['source_account_selected']:
                validation_results['issues'].append("Source account must be selected")
            
        except Exception as e:
            log.error(f"Open account form validation failed: {e}")
            validation_results['issues'].append(f"Validation error: {str(e)}")
        
        return validation_results

    def clear_open_account_form(self) -> None:
        """Clear open account form selections."""
        try:
            # Reset select elements to first option
            self.page.select_option(self.ACCOUNT_TYPE_SELECT, index=0)
            self.page.select_option(self.FROM_ACCOUNT_SELECT, index=0)
            
            log.info("Cleared open account form")
        except Exception as e:
            log.error(f"Failed to clear open account form: {e}")

    def click_accounts_overview(self) -> None:
        """Click Accounts Overview link."""
        self.wait_helper.wait_for_and_click(self.ACCOUNTS_OVERVIEW_LINK)
        log.info("Clicked Accounts Overview link")

    def assert_open_account_page_loaded(self) -> None:
        """Assert that open account page is properly loaded."""
        required_elements = [
            self.ACCOUNT_TYPE_SELECT,
            self.FROM_ACCOUNT_SELECT,
            self.OPEN_NEW_ACCOUNT_BUTTON
        ]
        
        for element in required_elements:
            self.assert_helper.assert_element_visible(element)
        
        self.assert_helper.assert_element_clickable(self.OPEN_NEW_ACCOUNT_BUTTON)
        log.info("Open account page loaded successfully")

    def assert_account_opened_successfully(self) -> None:
        """Assert that account was opened successfully."""
        self.assert_helper.assert_element_visible(self.SUCCESS_MESSAGE)
        
        success_text = self.get_text(self.SUCCESS_MESSAGE)
        assert "Account Opened!" in success_text or "successfully" in success_text.lower(), \
            "Account opening success message not found"
        
        # Also check for account details
        self.assert_helper.assert_element_visible(self.ACCOUNT_DETAILS)
        log.info("Account opening success assertion verified")

    def assert_account_opening_failed(self, expected_error: Optional[str] = None) -> None:
        """Assert that account opening failed with expected error."""
        self.assert_helper.assert_element_visible(self.ERROR_MESSAGE)
        
        if expected_error:
            self.assert_helper.assert_element_contains_text(self.ERROR_MESSAGE, expected_error)
        
        log.info("Account opening failure assertion verified")

    def wait_for_account_opening_complete(self, timeout: int = 10000) -> bool:
        """Wait for account opening process to complete."""
        try:
            return self.wait_helper.wait_for_custom_condition(
                condition=lambda: (
                    self.is_visible(self.SUCCESS_MESSAGE, timeout=1000) or 
                    self.is_visible(self.ERROR_MESSAGE, timeout=1000)
                ),
                timeout=timeout,
                message="Account opening completion timeout"
            )
        except:
            return False

    def validate_account_type_availability(self, account_type: str) -> bool:
        """Check if specific account type is available."""
        available_types = self.get_account_types()
        return account_type in available_types

    def validate_source_account_availability(self, account_id: str) -> bool:
        """Check if specific source account is available."""
        available_accounts = self.get_source_accounts()
        return account_id in available_accounts

    def simulate_account_opening_with_validation(
        self,
        account_type: str,
        source_account: str
    ) -> Dict[str, Any]:
        """Simulate account opening with comprehensive validation."""
        result = {
            'success': False,
            'error_message': None,
            'validation_results': None,
            'new_account_details': None,
            'timestamp': None
        }
        
        try:
            # Validate form before submission
            validation_results = self.validate_open_account_form()
            result['validation_results'] = validation_results
            
            if not validation_results['form_ready']:
                result['error_message'] = "Form validation failed: " + "; ".join(validation_results['issues'])
                return result
            
            # Validate availability
            if not self.validate_account_type_availability(account_type):
                result['error_message'] = f"Account type '{account_type}' is not available"
                return result
            
            if not self.validate_source_account_availability(source_account):
                result['error_message'] = f"Source account '{source_account}' is not available"
                return result
            
            # Perform account opening
            self.open_new_account(account_type, source_account)
            
            # Wait for completion
            opening_complete = self.wait_for_account_opening_complete()
            
            if opening_complete:
                if self.is_account_opened_successfully():
                    result['success'] = True
                    result['new_account_details'] = self.get_new_account_details()
                    log.info("Account opening simulation successful")
                else:
                    result['error_message'] = self.get_error_message()
                    log.warning(f"Account opening simulation failed: {result['error_message']}")
            
        except Exception as e:
            result['error_message'] = str(e)
            log.error(f"Account opening simulation exception: {e}")
        
        return result

    def get_account_opening_summary(self) -> Dict[str, Any]:
        """Get summary of account opening process."""
        try:
            summary = {
                'available_account_types': self.get_account_types(),
                'available_source_accounts': self.get_source_accounts(),
                'form_validation': self.validate_open_account_form(),
                'current_selections': {
                    'account_type': self.get_attribute(self.ACCOUNT_TYPE_SELECT, "value"),
                    'source_account': self.get_attribute(self.FROM_ACCOUNT_SELECT, "value")
                }
            }
            
            return summary
            
        except Exception as e:
            log.error(f"Failed to get account opening summary: {e}")
            return {}
