"""ParaBank Accounts Overview Page Object Model."""
from typing import Optional, Dict, Any, List
from playwright.sync_api import Page
from src.pages.base_page import BasePage
from src.utils.wait_helpers import WaitHelper, WaitStrategy
from src.utils.assertion_helpers import AssertionHelper
from src.utils.retry_handler import retry_with_backoff
from src.config.logger import log


class AccountsOverviewPage(BasePage):
    """Enterprise-grade Accounts Overview page object for ParaBank."""

    # Locators
    ACCOUNTS_TABLE = "#accountTable"
    ACCOUNT_ROWS = "#accountTable tbody tr"
    ACCOUNT_LINKS = "#accountTable tbody tr td:nth-child(1) a"
    BALANCE_VALUES = "#accountTable tbody tr td:nth-child(2)"
    ACCOUNT_TYPES = "#accountTable tbody tr td:nth-child(3)"
    OPEN_NEW_ACCOUNT_BUTTON = "a[href*='openaccount.htm']"
    TRANSFER_FUNDS_BUTTON = "a[href*='transfer.htm']"
    BILL_PAY_BUTTON = "a[href*='billpay.htm']"
    FIND_TRANSACTIONS_BUTTON = "a[href*='findtrans.htm']"
    LOGOUT_BUTTON = "a[href*='logout.htm']"
    WELCOME_MESSAGE = "#rightPanel h1:has-text('Accounts Overview')"
    TOTAL_BALANCE = "#accountTable tfoot tr td:nth-child(2)"
    NO_ACCOUNTS_MESSAGE = "#accountTable tbody tr td"
    ACCOUNT_DETAILS_HEADER = "#accountDetails h1"

    def __init__(self, page: Page):
        """Initialize Accounts Overview page with enterprise features."""
        super().__init__(page)
        self.wait_helper = WaitHelper(page)
        self.assert_helper = AssertionHelper(page)
        self.page_url = "parabank/overview.htm"

    @retry_with_backoff(max_attempts=3, base_delay=0.5)
    def navigate_to_accounts_overview(self) -> None:
        """Navigate to accounts overview page with retry mechanism."""
        self.goto(f"{self.page.url or ''}")

        self.wait_helper.wait_for_element(self.ACCOUNTS_TABLE, WaitStrategy.ELEMENT_VISIBLE, timeout=10000)
        log.info("Successfully navigated to accounts overview page")

    def get_all_accounts(self) -> List[Dict[str, str]]:
        """
        Get all account information from the accounts table.
        
        Returns:
            List of dictionaries containing account details
        """
        accounts = []
        
        try:
            # Wait for table to be visible
            self.wait_helper.wait_for_element(self.ACCOUNT_ROWS, WaitStrategy.ELEMENT_VISIBLE)
            
            # Get all account rows
            rows = self.find_elements(self.ACCOUNT_ROWS)
            
            for i, row in enumerate(rows):
                try:
                    # Extract account details from each row
                    account_id = row.locator("td:nth-child(1) a").text_content()
                    balance = row.locator("td:nth-child(2)").text_content()
                    account_type = row.locator("td:nth-child(3)").text_content()
                    
                    accounts.append({
                        'account_id': account_id.strip() if account_id else "",
                        'balance': balance.strip() if balance else "",
                        'account_type': account_type.strip() if account_type else "",
                        'row_index': i
                    })
                except Exception as e:
                    log.warning(f"Failed to extract account from row {i}: {e}")
                    continue
            
            log.info(f"Retrieved {len(accounts)} accounts")
            return accounts
            
        except Exception as e:
            log.error(f"Failed to get accounts: {e}")
            return []

    def get_account_by_id(self, account_id: str) -> Optional[Dict[str, str]]:
        """
        Get specific account information by account ID.
        
        Args:
            account_id: Account ID to search for
            
        Returns:
            Account information dictionary or None if not found
        """
        accounts = self.get_all_accounts()
        
        for account in accounts:
            if account['account_id'] == account_id:
                return account
        
        return None

    def get_account_count(self) -> int:
        """Get total number of accounts."""
        try:
            rows = self.find_elements(self.ACCOUNT_ROWS)
            return len(rows)
        except:
            return 0

    def get_total_balance(self) -> str:
        """Get total balance from the table footer."""
        try:
            if self.is_visible(self.TOTAL_BALANCE, timeout=5000):
                return self.get_text(self.TOTAL_BALANCE).strip()
            return ""
        except:
            return ""

    def click_account(self, account_id: str) -> None:
        """
        Click on a specific account to view details.
        
        Args:
            account_id: Account ID to click
        """
        try:
            # Find and click the account link
            account_link = f"#accountTable tbody tr td a:has-text('{account_id}')"
            self.wait_helper.wait_for_and_click(account_link)
            log.info(f"Clicked on account: {account_id}")
        except Exception as e:
            log.error(f"Failed to click account {account_id}: {e}")
            raise

    def click_open_new_account(self) -> None:
        """Click Open New Account button."""
        self.wait_helper.wait_for_and_click(self.OPEN_NEW_ACCOUNT_BUTTON)
        log.info("Clicked Open New Account button")

    def click_transfer_funds(self) -> None:
        """Click Transfer Funds button."""
        self.wait_helper.wait_for_and_click(self.TRANSFER_FUNDS_BUTTON)
        log.info("Clicked Transfer Funds button")

    def click_bill_pay(self) -> None:
        """Click Bill Pay button."""
        self.wait_helper.wait_for_and_click(self.BILL_PAY_BUTTON)
        log.info("Clicked Bill Pay button")

    def click_find_transactions(self) -> None:
        """Click Find Transactions button."""
        self.wait_helper.wait_for_and_click(self.FIND_TRANSACTIONS_BUTTON)
        log.info("Clicked Find Transactions button")

    def click_logout(self) -> None:
        """Click Logout button."""
        self.wait_helper.wait_for_and_click(self.LOGOUT_BUTTON)
        log.info("Clicked Logout button")

    def is_accounts_table_visible(self) -> bool:
        """Check if accounts table is visible."""
        return self.is_visible(self.ACCOUNTS_TABLE)

    def has_accounts(self) -> bool:
        """Check if user has any accounts."""
        try:
            # Check if there are account rows or if it shows no accounts message
            rows = self.find_elements(self.ACCOUNT_ROWS)
            if len(rows) > 0:
                return True
            
            # Check for no accounts message
            if self.is_visible(self.NO_ACCOUNTS_MESSAGE):
                no_accounts_text = self.get_text(self.NO_ACCOUNTS_MESSAGE).lower()
                return "no accounts" not in no_accounts_text
            
            return False
        except:
            return False

    def get_welcome_message(self) -> str:
        """Get welcome message."""
        try:
            if self.is_visible(self.WELCOME_MESSAGE, timeout=5000):
                return self.get_text(self.WELCOME_MESSAGE)
            return ""
        except:
            return ""

    def search_accounts_by_type(self, account_type: str) -> List[Dict[str, str]]:
        """
        Search accounts by account type.
        
        Args:
            account_type: Account type to filter by (e.g., 'Checking', 'Savings')
            
        Returns:
            List of matching accounts
        """
        all_accounts = self.get_all_accounts()
        return [
            account for account in all_accounts 
            if account_type.lower() in account['account_type'].lower()
        ]

    def get_accounts_with_minimum_balance(self, min_balance: float) -> List[Dict[str, str]]:
        """
        Get accounts with balance above minimum threshold.
        
        Args:
            min_balance: Minimum balance threshold
            
        Returns:
            List of accounts meeting criteria
        """
        qualifying_accounts = []
        
        for account in self.get_all_accounts():
            try:
                balance_str = account['balance'].replace('$', '').replace(',', '')
                balance = float(balance_str)
                if balance >= min_balance:
                    account['numeric_balance'] = balance
                    qualifying_accounts.append(account)
            except ValueError:
                log.warning(f"Could not parse balance for account {account['account_id']}")
                continue
        
        return qualifying_accounts

    def validate_account_data_integrity(self) -> Dict[str, Any]:
        """
        Validate account data integrity and consistency.
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'all_accounts_have_ids': True,
            'all_accounts_have_balances': True,
            'all_accounts_have_types': True,
            'balance_format_valid': True,
            'total_balance_calculable': True,
            'duplicate_accounts': False,
            'issues_found': []
        }
        
        try:
            accounts = self.get_all_accounts()
            account_ids = []
            
            for account in accounts:
                # Check required fields
                if not account['account_id']:
                    validation_results['all_accounts_have_ids'] = False
                    validation_results['issues_found'].append("Account missing ID")
                
                if not account['balance']:
                    validation_results['all_accounts_have_balances'] = False
                    validation_results['issues_found'].append("Account missing balance")
                
                if not account['account_type']:
                    validation_results['all_accounts_have_types'] = False
                    validation_results['issues_found'].append("Account missing type")
                
                # Check balance format
                if account['balance']:
                    try:
                        balance_str = account['balance'].replace('$', '').replace(',', '')
                        float(balance_str)
                    except ValueError:
                        validation_results['balance_format_valid'] = False
                        validation_results['issues_found'].append(f"Invalid balance format: {account['balance']}")
                
                # Check for duplicates
                if account['account_id'] in account_ids:
                    validation_results['duplicate_accounts'] = True
                    validation_results['issues_found'].append(f"Duplicate account ID: {account['account_id']}")
                else:
                    account_ids.append(account['account_id'])
            
            # Check if total balance can be calculated
            try:
                total = 0.0
                for account in accounts:
                    if account['balance']:
                        balance_str = account['balance'].replace('$', '').replace(',', '')
                        total += float(balance_str)
                validation_results['calculated_total'] = total
            except:
                validation_results['total_balance_calculable'] = False
                validation_results['issues_found'].append("Cannot calculate total balance")
            
        except Exception as e:
            log.error(f"Account data validation failed: {e}")
            validation_results['issues_found'].append(f"Validation error: {str(e)}")
        
        return validation_results

    def assert_accounts_overview_loaded(self) -> None:
        """Assert that accounts overview page is properly loaded."""
        self.assert_helper.assert_element_visible(self.ACCOUNTS_TABLE)
        self.assert_helper.assert_element_visible(self.WELCOME_MESSAGE)
        
        # Check for navigation buttons
        navigation_buttons = [
            self.OPEN_NEW_ACCOUNT_BUTTON,
            self.TRANSFER_FUNDS_BUTTON,
            self.BILL_PAY_BUTTON,
            self.FIND_TRANSACTIONS_BUTTON,
            self.LOGOUT_BUTTON
        ]
        
        for button in navigation_buttons:
            self.assert_helper.assert_element_visible(button)
        
        log.info("Accounts overview page loaded successfully")

    def assert_account_exists(self, account_id: str) -> None:
        """Assert that specific account exists in the table."""
        account = self.get_account_by_id(account_id)
        assert account is not None, f"Account {account_id} not found in accounts overview"
        log.info(f"Account {account_id} exists as expected")

    def assert_no_accounts_message(self) -> None:
        """Assert that no accounts message is displayed."""
        self.assert_helper.assert_element_visible(self.NO_ACCOUNTS_MESSAGE)
        no_accounts_text = self.get_text(self.NO_ACCOUNTS_MESSAGE).lower()
        assert "no accounts" in no_accounts_text, "No accounts message not found"
        log.info("No accounts message displayed as expected")

    def wait_for_accounts_load(self, timeout: int = 10000) -> bool:
        """Wait for accounts to load in the table."""
        try:
            return self.wait_helper.wait_for_custom_condition(
                condition=lambda: (
                    self.is_visible(self.ACCOUNTS_TABLE, timeout=1000) and
                    len(self.find_elements(self.ACCOUNT_ROWS)) > 0
                ),
                timeout=timeout,
                message="Accounts loading timeout"
            )
        except:
            return False

    def export_accounts_data(self) -> Dict[str, Any]:
        """
        Export accounts data for reporting or analysis.
        
        Returns:
            Dictionary with comprehensive accounts data
        """
        try:
            accounts = self.get_all_accounts()
            total_balance = self.get_total_balance()
            welcome_message = self.get_welcome_message()
            
            export_data = {
                'timestamp': self.page.evaluate("new Date().toISOString()"),
                'welcome_message': welcome_message,
                'total_accounts': len(accounts),
                'total_balance_displayed': total_balance,
                'accounts': accounts,
                'validation_results': self.validate_account_data_integrity()
            }
            
            log.info(f"Exported data for {len(accounts)} accounts")
            return export_data
            
        except Exception as e:
            log.error(f"Failed to export accounts data: {e}")
            return {}
