"""ParaBank Find Transactions Page Object Model."""

from typing import Optional, Dict, Any, List

from playwright.sync_api import Page

from src.pages.base_page import BasePage
from src.utils.wait_helpers import WaitHelper, WaitStrategy
from src.utils.assertion_helpers import AssertionHelper
from src.utils.retry_handler import retry_with_backoff
from src.config.logger import log
from src.config.settings import get_settings


class FindTransactionsPage(BasePage):
    """Enterprise-grade Find Transactions page object for ParaBank."""

    # =========================================================================
    # LOCATORS
    # =========================================================================

    ACCOUNT_SELECT = "#accountId"
    ACCOUNT_DROPDOWN = "#accountId"

    TRANSACTION_ID_FIELD = "#transactionForm #transactionId"
    DATE_FIELD = "#transactionForm #transactionDate"
    FROM_DATE_FIELD = "#transactionForm #fromDate"
    TO_DATE_FIELD = "#transactionForm #toDate"
    AMOUNT_FIELD = "#transactionForm #amount"

    FIND_BY_ID_BUTTON = "#transactionForm #findById"
    FIND_BY_DATE_BUTTON = "#transactionForm #findByDate"
    FIND_BY_DATE_RANGE_BUTTON = "#transactionForm #findByDateRange"
    FIND_BY_AMOUNT_BUTTON = "#transactionForm #findByAmount"

    RESULTS_TABLE = "#transactionTable"
    TRANSACTION_ROWS = "#transactionTable tbody tr"

    NO_RESULTS_MESSAGE = "text=No transactions found"

    ACCOUNTS_OVERVIEW_LINK = "a[href*='overview.htm']"

    # =========================================================================
    # INITIALIZATION
    # =========================================================================

    def __init__(self, page: Page):
        super().__init__(page)

        self.wait_helper = WaitHelper(page)
        self.assert_helper = AssertionHelper(page)
        self.page_url = "parabank/findtrans.htm"

    # =========================================================================
    # NAVIGATION
    # =========================================================================

    @retry_with_backoff(max_attempts=3, base_delay=0.5)
    def navigate_to_find_transactions(self) -> None:
        """Navigate to Find Transactions page."""

        try:
            settings = get_settings()

            self.goto(f"{settings.base_url}/findtrans.htm")

            self.page.wait_for_load_state("networkidle")

            self.assert_helper.assert_element_visible(
                self.ACCOUNT_SELECT
            )

            self.assert_helper.assert_element_visible(
                self.FIND_BY_ID_BUTTON
            )

            log.info(
                "Successfully navigated to Find Transactions page"
            )

        except Exception as e:
            log.error(
                f"Navigation to Find Transactions page failed: {e}"
            )
            raise

    # =========================================================================
    # PAGE VALIDATION
    # =========================================================================

    def assert_find_transactions_page_loaded(self) -> None:
        """Assert Find Transactions page loaded successfully."""

        required_elements = [
            self.ACCOUNT_SELECT,
            self.FIND_BY_ID_BUTTON,
        ]

        for element in required_elements:
            self.assert_helper.assert_element_visible(element)

        self.assert_helper.assert_element_is_clickable(
            self.FIND_BY_ID_BUTTON
        )

        log.info(
            "Find Transactions page loaded successfully"
        )

    # =========================================================================
    # ACCOUNT METHODS
    # =========================================================================

    def get_available_accounts(self) -> List[str]:
        """Get all available account IDs."""

        try:
            self.wait_helper.wait_for_element(
                self.ACCOUNT_SELECT,
                WaitStrategy.ELEMENT_VISIBLE
            )

            options = self.page.locator(
                f"{self.ACCOUNT_SELECT} option"
            )

            account_ids = []

            for i in range(options.count()):
                option = options.nth(i)

                value = option.get_attribute("value")
                text = option.text_content()

                account_id = (
                    value.strip()
                    if value and value.strip()
                    else text.strip() if text else ""
                )

                if account_id:
                    account_ids.append(account_id)

            log.info(
                f"Found {len(account_ids)} accounts"
            )

            return account_ids

        except Exception as e:
            log.error(
                f"Failed to get available accounts: {e}"
            )
            return []

    def select_account(self, account_id: str) -> None:
        """Select account."""

        try:
            self.wait_helper.wait_for_element(
                self.ACCOUNT_SELECT,
                WaitStrategy.ELEMENT_VISIBLE
            )

            self.page.select_option(
                self.ACCOUNT_SELECT,
                value=str(account_id)
            )

            log.info(
                f"Selected account: {account_id}"
            )

        except Exception:
            try:
                self.page.select_option(
                    self.ACCOUNT_SELECT,
                    label=str(account_id)
                )

                log.info(
                    f"Selected account by label: {account_id}"
                )

            except Exception as e:
                log.error(
                    f"Failed to select account "
                    f"{account_id}: {e}"
                )
                raise

    # =========================================================================
    # INPUT METHODS
    # =========================================================================

    def enter_transaction_id(
        self,
        transaction_id: str
    ) -> None:
        """Enter transaction ID."""

        self.wait_helper.wait_for_element(
            self.TRANSACTION_ID_FIELD,
            WaitStrategy.ELEMENT_VISIBLE
        )

        self.fill(
            self.TRANSACTION_ID_FIELD,
            transaction_id
        )

        log.info(
            f"Entered transaction ID: {transaction_id}"
        )

    def enter_date(self, date: str) -> None:
        """Enter transaction date."""

        self.wait_helper.wait_for_element(
            self.DATE_FIELD,
            WaitStrategy.ELEMENT_VISIBLE
        )

        self.fill(self.DATE_FIELD, date)

        log.info(f"Entered transaction date: {date}")

    def enter_date_range(
        self,
        from_date: str,
        to_date: str
    ) -> None:
        """Enter date range."""

        self.wait_helper.wait_for_element(
            self.FROM_DATE_FIELD,
            WaitStrategy.ELEMENT_VISIBLE
        )

        self.fill(
            self.FROM_DATE_FIELD,
            from_date
        )

        self.fill(
            self.TO_DATE_FIELD,
            to_date
        )

        log.info(
            f"Entered date range: "
            f"{from_date} - {to_date}"
        )

    def enter_amount(self, amount: str) -> None:
        """Enter transaction amount."""

        self.wait_helper.wait_for_element(
            self.AMOUNT_FIELD,
            WaitStrategy.ELEMENT_VISIBLE
        )

        self.fill(self.AMOUNT_FIELD, amount)

        log.info(f"Entered amount: {amount}")

    # =========================================================================
    # SEARCH METHODS
    # =========================================================================

    # def search_transactions(
    #     self,
    #     account_id: Optional[str] = None,
    #     transaction_id: Optional[str] = None,
    #     date: Optional[str] = None,
    #     from_date: Optional[str] = None,
    #     to_date: Optional[str] = None,
    #     amount: Optional[str] = None,
    # ) -> None:
    #     """
    #     Search transactions using provided criteria.
    #     """

    #     try:
    #         if account_id:
    #             self.select_account(account_id)

    #         if transaction_id:
    #             self.enter_transaction_id(
    #                 transaction_id
    #             )

    #         if date:
    #             self.enter_date(date)

    #         if from_date and to_date:
    #             self.enter_date_range(
    #                 from_date,
    #                 to_date
    #             )

    #         if amount:
    #             self.enter_amount(amount)

    #         self.click_find_transactions(
    #             transaction_id=transaction_id,
    #             date=date,
    #             from_date=from_date,
    #             to_date=to_date,
    #             amount=amount,
    #         )

    #         log.info(
    #             "Transaction search initiated"
    #         )

    #     except Exception as e:
    #         log.error(
    #             f"Transaction search failed: {e}"
    #         )
    #         raise

    def search_transactions(
        self,
        account_id: Optional[str] = None,
        transaction_id: Optional[str] = None,
        date: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        amount: Optional[str] = None,
    ) -> None:
        """
        Search transactions using provided criteria.

        Backward compatible:
        - supports account-only searches
        - supports ID/date/range/amount searches
        - stable for parallel + mobile suites
        """

        try:

            # =====================================================
            # FILL SEARCH FORM
            # =====================================================

            if account_id:
                self.select_account(account_id)

            if transaction_id:
                self.enter_transaction_id(
                    transaction_id
                )

            if date:
                self.enter_date(date)

            if from_date or to_date:
                self.enter_date_range(
                    from_date or "",
                    to_date or ""
                )

            if amount:
                self.enter_amount(amount)

            # =====================================================
            # DETERMINE SEARCH TYPE
            # =====================================================

            has_advanced_criteria = any([
                transaction_id,
                date,
                from_date,
                to_date,
                amount,
            ])

            # =====================================================
            # ACCOUNT-ONLY SEARCH
            #
            # IMPORTANT:
            # Older stable suites rely on this behavior.
            # ParaBank still requires a search button click even
            # when only account is selected.
            # =====================================================

            if account_id and not has_advanced_criteria:

                self.click_find_transactions(
                    date="account_search_fallback"
                )

            # =====================================================
            # TRANSACTION ID SEARCH
            # =====================================================

            elif transaction_id:

                self.click_find_transactions(
                    transaction_id=transaction_id
                )

            # =====================================================
            # EXACT DATE SEARCH
            # =====================================================

            elif date:

                self.click_find_transactions(
                    date=date
                )

            # =====================================================
            # DATE RANGE SEARCH
            # =====================================================

            elif from_date or to_date:

                self.click_find_transactions(
                    from_date=from_date,
                    to_date=to_date,
                )

            # =====================================================
            # AMOUNT SEARCH
            # =====================================================

            elif amount:

                self.click_find_transactions(
                    amount=amount
                )

            # =====================================================
            # INVALID SEARCH
            # =====================================================

            else:
                raise ValueError(
                    "At least one search criteria must be provided"
                )

            log.info(
                "Transaction search initiated"
            )

        except Exception as e:

            log.error(
                f"Transaction search failed: {e}"
            )

            raise


    def click_find_transactions(
        self,
        transaction_id: Optional[str] = None,
        date: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        amount: Optional[str] = None,
    ) -> None:
        """Click appropriate Find Transactions button."""

        if transaction_id:
            button = self.FIND_BY_ID_BUTTON

        elif date:
            button = self.FIND_BY_DATE_BUTTON

        elif from_date and to_date:
            button = self.FIND_BY_DATE_RANGE_BUTTON

        elif amount:
            button = self.FIND_BY_AMOUNT_BUTTON

        else:
            raise ValueError(
                "At least one search criteria "
                "must be provided"
            )

        self.wait_helper.wait_for_element(
            button,
            WaitStrategy.ELEMENT_CLICKABLE
        )

        self.click(button)

        log.info(
            f"Clicked Find Transactions button: "
            f"{button}"
        )

    # def wait_for_search_results(self, timeout: int = 10000) -> bool:
    #     """Wait for search results state."""

    #     try:
    #         self.page.wait_for_function(
    #             """
    #             () => {
    #                 const tableRows =
    #                     document.querySelectorAll(
    #                         '#transactionTable tbody tr'
    #                     ).length > 0;

    #                 const noResults =
    #                     document.body.innerText.includes(
    #                         'No transactions found'
    #                     );

    #                 return tableRows || noResults;
    #             }
    #             """,
    #             timeout=timeout
    #         )

    #         log.info("Search results loaded")

    #         return True

    #     except Exception as e:
    #         log.error(
    #             f"Search results wait failed: {e}"
    #         )

    #     return False

    def wait_for_search_results(
        self,
        timeout: int = 10000
    ) -> bool:
        """
        Wait for transaction search results.

        Supports:
        - transaction table
        - no results message
        - account-only search refresh
        """

        try:

            self.page.wait_for_load_state(
                "networkidle",
                timeout=timeout
            )

            # ==========================================
            # RESULTS TABLE
            # ==========================================

            if self.is_visible(
                self.RESULTS_TABLE,
                timeout=3000
            ):
                return True

            # ==========================================
            # NO RESULTS MESSAGE
            # ==========================================

            if self.is_no_results_visible():
                return True

            # ==========================================
            # FALLBACK:
            # ParaBank sometimes refreshes content
            # without changing DOM significantly.
            # ==========================================

            content = self.page.content().lower()

            fallback_indicators = [
                "transaction results",
                "transaction id",
                "date",
                "amount",
                "results"
            ]

            if any(
                text in content
                for text in fallback_indicators
            ):
                return True

            return False

        except Exception as e:

            log.error(
                f"Search results wait failed: {e}"
            )

            return False
    # =========================================================================
    # TRANSACTION DATA METHODS
    # =========================================================================

    def get_transactions(
        self
    ) -> List[Dict[str, str]]:
        """Get transaction rows from results table."""

        transactions = []

        try:
            if not self.is_visible(
                self.RESULTS_TABLE,
                timeout=5000
            ):
                return transactions

            rows = self.page.locator(
                self.TRANSACTION_ROWS
            )

            row_count = rows.count()

            for i in range(row_count):

                try:
                    row = rows.nth(i)

                    cells = row.locator("td")

                    if cells.count() < 5:
                        continue

                    transaction = {
                        "transaction_id": (
                            cells.nth(0)
                            .text_content() or ""
                        ).strip(),

                        "date": (
                            cells.nth(1)
                            .text_content() or ""
                        ).strip(),

                        "description": (
                            cells.nth(2)
                            .text_content() or ""
                        ).strip(),

                        "deposit": (
                            cells.nth(3)
                            .text_content() or ""
                        ).strip(),

                        "withdrawal": (
                            cells.nth(4)
                            .text_content() or ""
                        ).strip(),

                        "row_index": i,
                    }

                    transactions.append(transaction)

                except Exception as row_error:
                    log.warning(
                        f"Failed to parse "
                        f"transaction row {i}: "
                        f"{row_error}"
                    )

            log.info(
                f"Retrieved "
                f"{len(transactions)} transactions"
            )

            return transactions

        except Exception as e:
            log.error(
                f"Failed to retrieve transactions: {e}"
            )
            return []

    def get_transaction_count(self) -> int:
        """Get number of transaction rows."""

        try:
            return self.page.locator(
                self.TRANSACTION_ROWS
            ).count()

        except Exception:
            return 0

    # def has_transactions(self) -> bool:
    #     """Check if transactions table has rows."""

    #     try:
    #         if not self.page.is_visible(
    #             self.RESULTS_TABLE
    #         ):
    #             return False

    #         rows = self.page.locator(
    #             f"{self.RESULTS_TABLE} tbody tr"
    #         )

    #         return rows.count() > 0

    #     except Exception:
    #         return False

    def has_transactions(self) -> bool:
        """Check if transaction rows exist."""

        try:
            rows = self.page.locator(
                f"{self.RESULTS_TABLE} tbody tr"
            )

            return rows.count() > 0

        except Exception:
            return False

    def get_no_results_message(self) -> str:
        """Get no results message."""

        try:
            if self.is_visible(
                self.NO_RESULTS_MESSAGE,
                timeout=3000
            ):
                return self.get_text(
                    self.NO_RESULTS_MESSAGE
                )

            return ""

        except Exception:
            return ""

    # =========================================================================
    # SEARCH HELPERS
    # =========================================================================

    def search_by_transaction_id(
        self,
        transaction_id: str
    ) -> Optional[Dict[str, str]]:
        """Find transaction by ID."""

        transactions = self.get_transactions()

        for transaction in transactions:
            if (
                transaction["transaction_id"]
                == transaction_id
            ):
                return transaction

        return None

    def search_transactions_by_description(
        self,
        description_keyword: str
    ) -> List[Dict[str, str]]:
        """Search transactions by description keyword."""

        keyword = description_keyword.lower()

        return [
            transaction
            for transaction in self.get_transactions()
            if keyword in transaction[
                "description"
            ].lower()
        ]

    def get_transactions_by_amount_range(
        self,
        min_amount: float,
        max_amount: float
    ) -> List[Dict[str, str]]:
        """Get transactions within amount range."""

        matching_transactions = []

        for transaction in self.get_transactions():

            try:
                amounts = [
                    transaction.get("deposit", ""),
                    transaction.get("withdrawal", ""),
                ]

                for amount in amounts:

                    if not amount:
                        continue

                    cleaned_amount = (
                        amount
                        .replace("$", "")
                        .replace(",", "")
                        .strip()
                    )

                    amount_value = float(
                        cleaned_amount
                    )

                    if (
                        min_amount
                        <= amount_value
                        <= max_amount
                    ):
                        matching_transactions.append(
                            transaction
                        )
                        break

            except Exception:
                log.warning(
                    "Could not parse "
                    "transaction amount"
                )

        return matching_transactions

    # =========================================================================
    # VALIDATION METHODS
    # =========================================================================

    def validate_search_criteria(self) -> dict:
        """Validate entered search criteria."""

        amount_value = (
            self.page.locator(
                self.AMOUNT_FIELD
            )
            .input_value()
            .strip()
        )

        account_value = (
            self.page.locator(
                self.ACCOUNT_DROPDOWN
            )
            .input_value()
            .strip()
        )

        valid_amount = True

        if amount_value:
            try:
                float(amount_value)

            except ValueError:
                valid_amount = False

        account_selected = (
            account_value != ""
            and account_value.lower() != "select"
        )

        return {
            "account_selected": account_selected,
            "valid_amount": valid_amount,
            "search_ready": (
                account_selected and valid_amount
            ),
        }

    # =========================================================================
    # FORM METHODS
    # =========================================================================

    def clear_search_form(self) -> None:
        """Clear search form."""

        try:
            fields = [
                self.TRANSACTION_ID_FIELD,
                self.DATE_FIELD,
                self.FROM_DATE_FIELD,
                self.TO_DATE_FIELD,
                self.AMOUNT_FIELD,
            ]

            for field in fields:
                if self.is_visible(
                    field,
                    timeout=1000
                ):
                    self.fill(field, "")

            if self.is_visible(
                self.ACCOUNT_SELECT,
                timeout=1000
            ):
                self.page.select_option(
                    self.ACCOUNT_SELECT,
                    index=0
                )

            log.info("Cleared search form")

        except Exception as e:
            log.error(
                f"Failed to clear form: {e}"
            )

    # =========================================================================
    # NAVIGATION ACTIONS
    # =========================================================================

    def click_accounts_overview(self) -> None:
        """Navigate to Accounts Overview page."""

        self.wait_helper.wait_for_and_click(
            self.ACCOUNTS_OVERVIEW_LINK
        )

        log.info(
            "Clicked Accounts Overview link"
        )

    # =========================================================================
    # ASSERTION METHODS
    # =========================================================================

    def assert_transactions_found(
        self,
        min_count: int = 1
    ) -> None:
        """Assert transactions exist."""

        transaction_count = (
            self.get_transaction_count()
        )

        assert transaction_count >= min_count, (
            f"Expected at least {min_count} "
            f"transactions, found "
            f"{transaction_count}"
        )

        log.info(
            f"Verified {transaction_count} "
            f"transactions found"
        )

    def assert_no_transactions_found(self) -> None:
        """Assert no transactions found."""

        message = (
            self.get_no_results_message()
            .lower()
        )

        assert (
            "no results" in message
            or "no transactions" in message
        ), (
            "Expected no transactions message "
            "not displayed"
        )

        log.info(
            "Verified no transactions found"
        )

    # =========================================================================
    # EXPORT METHODS
    # =========================================================================

    def export_transaction_data(
        self
    ) -> Dict[str, Any]:
        """Export transaction data."""

        try:
            export_data = {
                "timestamp": self.page.evaluate(
                    "() => new Date().toISOString()"
                ),

                "total_transactions": (
                    self.get_transaction_count()
                ),

                "transactions": (
                    self.get_transactions()
                ),

                "search_criteria": {
                    "account": self.get_attribute(
                        self.ACCOUNT_SELECT,
                        "value"
                    ),

                    "transaction_id": (
                        self.get_attribute(
                            self.TRANSACTION_ID_FIELD,
                            "value"
                        )
                    ),

                    "date": self.get_attribute(
                        self.DATE_FIELD,
                        "value"
                    ),

                    "from_date": (
                        self.get_attribute(
                            self.FROM_DATE_FIELD,
                            "value"
                        )
                    ),

                    "to_date": self.get_attribute(
                        self.TO_DATE_FIELD,
                        "value"
                    ),

                    "amount": self.get_attribute(
                        self.AMOUNT_FIELD,
                        "value"
                    ),
                },
            }

            log.info(
                "Successfully exported "
                "transaction data"
            )

            return export_data

        except Exception as e:
            log.error(
                f"Failed to export "
                f"transaction data: {e}"
            )

            return {}

    def is_no_results_visible(self) -> bool:
        """Check if no results message is displayed."""

        return self.page.is_visible(
            self.NO_RESULTS_MESSAGE
        )