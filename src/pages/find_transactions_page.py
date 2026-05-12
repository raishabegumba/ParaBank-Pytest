"""ParaBank Find Transactions Page Object Model."""
from typing import Optional, Dict, Any, List
from playwright.sync_api import Page
from src.pages.base_page import BasePage
from src.utils.wait_helpers import WaitHelper, WaitStrategy
from src.utils.assertion_helpers import AssertionHelper
from src.utils.retry_handler import retry_with_backoff
from src.config.logger import log


class FindTransactionsPage(BasePage):
    """Enterprise-grade Find Transactions page object for ParaBank."""

    # Locators
    ACCOUNT_SELECT = "#accountId"
    TRANSACTION_TYPE_SELECT = "#transactionType"
    DATE_SELECT = "#onDate"
    FROM_DATE_FIELD = "#fromDate"
    TO_DATE_FIELD = "#toDate"
    AMOUNT_FIELD = "#amount"
    FIND_TRANSACTIONS_BUTTON = "input[type='submit'][value='Find Transactions']"
    TRANSACTIONS_TABLE = "#transactionTable"
    TRANSACTION_ROWS = "#transactionTable tbody tr"
    NO_RESULTS_MESSAGE = "#transactionTable tbody tr td"
    SUCCESS_MESSAGE = "#rightPanel h1"
    ERROR_MESSAGE = ".error"
    ACCOUNTS_OVERVIEW_LINK = "a[href*='overview.htm']"
    TRANSACTION_ID_HEADER = "#transactionTable th:nth-child(1)"
    DATE_HEADER = "#transactionTable th:nth-child(2)"
    DESCRIPTION_HEADER = "#transactionTable th:nth-child(3)"
    DEPOSIT_HEADER = "#transactionTable th:nth-child(4)"
    WITHDRAWAL_HEADER = "#transactionTable th:nth-child(5)"

    def __init__(self, page: Page):
        """Initialize Find Transactions page with enterprise features."""
        super().__init__(page)
        self.wait_helper = WaitHelper(page)
        self.assert_helper = AssertionHelper(page)
        self.page_url = "parabank/findtrans.htm"

    @retry_with_backoff(max_attempts=3, base_delay=0.5)
    def navigate_to_find_transactions(self) -> None:
        """Navigate to find transactions page with retry mechanism."""
        self.goto(f"{self.page.context.browser._browser_options.base_url}/findtrans.htm")
        self.wait_helper.wait_for_element(self.ACCOUNT_SELECT, WaitStrategy.ELEMENT_VISIBLE)
        log.info("Successfully navigated to find transactions page")

    def get_available_accounts(self) -> List[str]:
        """Get list of available accounts for transaction search."""
        try:
            self.wait_helper.wait_for_element(self.ACCOUNT_SELECT, WaitStrategy.ELEMENT_VISIBLE)
            
            options = self.page.locator(f"{self.ACCOUNT_SELECT} option")
            account_ids = []
            
            for i in range(options.count()):
                option_text = options.nth(i).text_content()
                if option_text and option_text.strip():
                    account_ids.append(option_text.strip())
            
            log.info(f"Found {len(account_ids)} accounts for transaction search")
            return account_ids
            
        except Exception as e:
            log.error(f"Failed to get available accounts: {e}")
            return []

    def get_transaction_types(self) -> List[str]:
        """Get list of available transaction types."""
        try:
            self.wait_helper.wait_for_element(self.TRANSACTION_TYPE_SELECT, WaitStrategy.ELEMENT_VISIBLE)
            
            options = self.page.locator(f"{self.TRANSACTION_TYPE_SELECT} option")
            transaction_types = []
            
            for i in range(options.count()):
                option_text = options.nth(i).text_content()
                if option_text and option_text.strip():
                    transaction_types.append(option_text.strip())
            
            log.info(f"Found {len(transaction_types)} transaction types")
            return transaction_types
            
        except Exception as e:
            log.error(f"Failed to get transaction types: {e}")
            return []

    def select_account(self, account_id: str) -> None:
        """Select account for transaction search."""
        try:
            self.wait_helper.wait_for_element(self.ACCOUNT_SELECT, WaitStrategy.ELEMENT_VISIBLE)
            self.page.select_option(self.ACCOUNT_SELECT, account_id)
            log.info(f"Selected account: {account_id}")
        except Exception as e:
            log.error(f"Failed to select account {account_id}: {e}")
            raise

    def select_transaction_type(self, transaction_type: str) -> None:
        """Select transaction type filter."""
        try:
            self.wait_helper.wait_for_element(self.TRANSACTION_TYPE_SELECT, WaitStrategy.ELEMENT_VISIBLE)
            self.page.select_option(self.TRANSACTION_TYPE_SELECT, transaction_type)
            log.info(f"Selected transaction type: {transaction_type}")
        except Exception as e:
            log.error(f"Failed to select transaction type {transaction_type}: {e}")
            raise

    def enter_date(self, date: str) -> None:
        """Enter specific date for search."""
        self.wait_helper.wait_for_element(self.DATE_SELECT, WaitStrategy.ELEMENT_VISIBLE)
        self.fill(self.DATE_SELECT, date)
        log.info(f"Entered search date: {date}")

    def enter_date_range(self, from_date: str, to_date: str) -> None:
        """Enter date range for search."""
        try:
            self.wait_helper.wait_for_element(self.FROM_DATE_FIELD, WaitStrategy.ELEMENT_VISIBLE)
            self.wait_helper.wait_for_element(self.TO_DATE_FIELD, WaitStrategy.ELEMENT_VISIBLE)
            
            self.fill(self.FROM_DATE_FIELD, from_date)
            self.fill(self.TO_DATE_FIELD, to_date)
            
            log.info(f"Entered date range: {from_date} to {to_date}")
        except Exception as e:
            log.error(f"Failed to enter date range: {e}")
            raise

    def enter_amount(self, amount: str) -> None:
        """Enter amount for search."""
        self.wait_helper.wait_for_element(self.AMOUNT_FIELD, WaitStrategy.ELEMENT_VISIBLE)
        self.fill(self.AMOUNT_FIELD, amount)
        log.info(f"Entered search amount: {amount}")

    def search_transactions(
        self,
        account_id: Optional[str] = None,
        transaction_type: Optional[str] = None,
        date: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        amount: Optional[str] = None
    ) -> None:
        """
        Search transactions with various criteria.
        
        Args:
            account_id: Account ID to search
            transaction_type: Transaction type filter
            date: Specific date
            from_date: Start date for range
            to_date: End date for range
            amount: Transaction amount
        """
        try:
            if account_id:
                self.select_account(account_id)
            
            if transaction_type:
                self.select_transaction_type(transaction_type)
            
            if date:
                self.enter_date(date)
            elif from_date and to_date:
                self.enter_date_range(from_date, to_date)
            
            if amount:
                self.enter_amount(amount)
            
            self.click_find_transactions()
            log.info("Initiated transaction search")
            
        except Exception as e:
            log.error(f"Transaction search failed: {e}")
            raise

    def click_find_transactions(self) -> None:
        """Click find transactions button."""
        self.wait_helper.wait_for_element(self.FIND_TRANSACTIONS_BUTTON, WaitStrategy.ELEMENT_CLICKABLE)
        self.click(self.FIND_TRANSACTIONS_BUTTON)
        log.info("Clicked find transactions button")

    def get_transactions(self) -> List[Dict[str, str]]:
        """Get all transactions from the results table."""
        transactions = []
        
        try:
            # Wait for table to be visible
            if not self.is_visible(self.TRANSACTIONS_TABLE, timeout=5000):
                return transactions
            
            # Get all transaction rows
            rows = self.find_elements(self.TRANSACTION_ROWS)
            
            for i, row in enumerate(rows):
                try:
                    # Extract transaction details from each row
                    cells = row.locator("td")
                    
                    if cells.count() >= 5:
                        transaction_id = cells.nth(0).text_content()
                        date = cells.nth(1).text_content()
                        description = cells.nth(2).text_content()
                        deposit = cells.nth(3).text_content()
                        withdrawal = cells.nth(4).text_content()
                        
                        transactions.append({
                            'transaction_id': transaction_id.strip() if transaction_id else "",
                            'date': date.strip() if date else "",
                            'description': description.strip() if description else "",
                            'deposit': deposit.strip() if deposit else "",
                            'withdrawal': withdrawal.strip() if withdrawal else "",
                            'row_index': i
                        })
                except Exception as e:
                    log.warning(f"Failed to extract transaction from row {i}: {e}")
                    continue
            
            log.info(f"Retrieved {len(transactions)} transactions")
            return transactions
            
        except Exception as e:
            log.error(f"Failed to get transactions: {e}")
            return []

    def get_transaction_count(self) -> int:
        """Get total number of transactions found."""
        try:
            rows = self.find_elements(self.TRANSACTION_ROWS)
            return len(rows)
        except:
            return 0

    def has_transactions(self) -> bool:
        """Check if any transactions were found."""
        try:
            # Check if there are transaction rows
            rows = self.find_elements(self.TRANSACTION_ROWS)
            if len(rows) > 0:
                return True
            
            # Check for no results message
            if self.is_visible(self.NO_RESULTS_MESSAGE):
                no_results_text = self.get_text(self.NO_RESULTS_MESSAGE).lower()
                return "no results" not in no_results_text and "no transactions" not in no_results_text
            
            return False
        except:
            return False

    def get_no_results_message(self) -> str:
        """Get no results message."""
        try:
            if self.is_visible(self.NO_RESULTS_MESSAGE, timeout=3000):
                return self.get_text(self.NO_RESULTS_MESSAGE)
            return ""
        except:
            return ""

    def search_by_transaction_id(self, transaction_id: str) -> Optional[Dict[str, str]]:
        """Search for specific transaction by ID."""
        transactions = self.get_transactions()
        
        for transaction in transactions:
            if transaction['transaction_id'] == transaction_id:
                return transaction
        
        return None

    def search_transactions_by_description(self, description_keyword: str) -> List[Dict[str, str]]:
        """Search transactions containing specific description keyword."""
        all_transactions = self.get_transactions()
        
        return [
            transaction for transaction in all_transactions 
            if description_keyword.lower() in transaction['description'].lower()
        ]

    def get_transactions_by_amount_range(self, min_amount: float, max_amount: float) -> List[Dict[str, str]]:
        """Get transactions within specified amount range."""
        qualifying_transactions = []
        
        for transaction in self.get_transactions():
            try:
                # Check deposit amount
                if transaction['deposit']:
                    deposit_str = transaction['deposit'].replace('$', '').replace(',', '')
                    deposit_amount = float(deposit_str)
                    if min_amount <= deposit_amount <= max_amount:
                        qualifying_transactions.append(transaction)
                        continue
                
                # Check withdrawal amount
                if transaction['withdrawal']:
                    withdrawal_str = transaction['withdrawal'].replace('$', '').replace(',', '')
                    withdrawal_amount = float(withdrawal_str)
                    if min_amount <= withdrawal_amount <= max_amount:
                        qualifying_transactions.append(transaction)
                        
            except ValueError:
                log.warning(f"Could not parse amount for transaction {transaction['transaction_id']}")
                continue
        
        return qualifying_transactions

    def validate_search_criteria(self) -> Dict[str, Any]:
        """Validate search criteria before submission."""
        validation_results = {
            'account_selected': False,
            'valid_date_range': True,
            'valid_amount': True,
            'search_ready': False,
            'issues': []
        }
        
        try:
            # Check account selection
            account_value = self.get_attribute(self.ACCOUNT_SELECT, "value")
            validation_results['account_selected'] = bool(account_value and account_value.strip())
            
            # Validate date range if provided
            from_date = self.get_attribute(self.FROM_DATE_FIELD, "value")
            to_date = self.get_attribute(self.TO_DATE_FIELD, "value")
            
            if from_date and to_date:
                # Basic date validation - could be enhanced
                validation_results['valid_date_range'] = len(from_date) >= 6 and len(to_date) >= 6
                if not validation_results['valid_date_range']:
                    validation_results['issues'].append("Invalid date format")
            
            # Validate amount if provided
            amount_value = self.get_attribute(self.AMOUNT_FIELD, "value")
            if amount_value:
                try:
                    amount_float = float(amount_value.replace('$', '').replace(',', ''))
                    validation_results['valid_amount'] = amount_float > 0
                    if amount_float <= 0:
                        validation_results['issues'].append("Amount must be greater than 0")
                except ValueError:
                    validation_results['valid_amount'] = False
                    validation_results['issues'].append("Invalid amount format")
            
            # Overall search readiness
            validation_results['search_ready'] = (
                validation_results['account_selected'] and
                validation_results['valid_date_range'] and
                validation_results['valid_amount']
            )
            
        except Exception as e:
            log.error(f"Search criteria validation failed: {e}")
            validation_results['issues'].append(f"Validation error: {str(e)}")
        
        return validation_results

    def clear_search_form(self) -> None:
        """Clear all search form fields."""
        try:
            # Clear text fields
            self.fill(self.DATE_SELECT, "")
            self.fill(self.FROM_DATE_FIELD, "")
            self.fill(self.TO_DATE_FIELD, "")
            self.fill(self.AMOUNT_FIELD, "")
            
            # Reset select elements to first option (usually "All" or empty)
            self.page.select_option(self.ACCOUNT_SELECT, index=0)
            self.page.select_option(self.TRANSACTION_TYPE_SELECT, index=0)
            
            log.info("Cleared search form")
        except Exception as e:
            log.error(f"Failed to clear search form: {e}")

    def click_accounts_overview(self) -> None:
        """Click Accounts Overview link."""
        self.wait_helper.wait_for_and_click(self.ACCOUNTS_OVERVIEW_LINK)
        log.info("Clicked Accounts Overview link")

    def assert_find_transactions_page_loaded(self) -> None:
        """Assert that find transactions page is properly loaded."""
        required_elements = [
            self.ACCOUNT_SELECT,
            self.TRANSACTION_TYPE_SELECT,
            self.FIND_TRANSACTIONS_BUTTON
        ]
        
        for element in required_elements:
            self.assert_helper.assert_element_visible(element)
        
        self.assert_helper.assert_element_clickable(self.FIND_TRANSACTIONS_BUTTON)
        log.info("Find transactions page loaded successfully")

    def assert_transactions_found(self, min_count: int = 1) -> None:
        """Assert that transactions were found."""
        transaction_count = self.get_transaction_count()
        assert transaction_count >= min_count, f"Expected at least {min_count} transactions, found {transaction_count}"
        log.info(f"Found {transaction_count} transactions as expected")

    def assert_no_transactions_found(self) -> None:
        """Assert that no transactions were found."""
        no_results_message = self.get_no_results_message()
        assert "no results" in no_results_message.lower() or "no transactions" in no_results_message.lower(), \
            "Expected no transactions message not found"
        log.info("No transactions found as expected")

    def wait_for_search_results(self, timeout: int = 10000) -> bool:
        """Wait for search results to load."""
        try:
            return self.wait_helper.wait_for_custom_condition(
                condition=lambda: (
                    self.is_visible(self.TRANSACTIONS_TABLE, timeout=1000) or
                    self.is_visible(self.NO_RESULTS_MESSAGE, timeout=1000)
                ),
                timeout=timeout,
                message="Search results timeout"
            )
        except:
            return False

    def export_transaction_data(self) -> Dict[str, Any]:
        """Export transaction data for reporting or analysis."""
        try:
            transactions = self.get_transactions()
            
            export_data = {
                'timestamp': self.page.evaluate("new Date().toISOString()"),
                'total_transactions': len(transactions),
                'transactions': transactions,
                'search_criteria': {
                    'account': self.get_attribute(self.ACCOUNT_SELECT, "value"),
                    'transaction_type': self.get_attribute(self.TRANSACTION_TYPE_SELECT, "value"),
                    'date': self.get_attribute(self.DATE_SELECT, "value"),
                    'from_date': self.get_attribute(self.FROM_DATE_FIELD, "value"),
                    'to_date': self.get_attribute(self.TO_DATE_FIELD, "value"),
                    'amount': self.get_attribute(self.AMOUNT_FIELD, "value")
                }
            }
            
            log.info(f"Exported data for {len(transactions)} transactions")
            return export_data
            
        except Exception as e:
            log.error(f"Failed to export transaction data: {e}")
            return {}
