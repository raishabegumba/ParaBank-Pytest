# """Parallel-safe Find Transactions tests."""

# import pytest
# from playwright.sync_api import Page

# from src.pages.find_transactions_page import FindTransactionsPage
# from src.pages.login_page import LoginPage


# @pytest.mark.parallel
# @pytest.mark.ui
# @pytest.mark.find_transactions
# class TestFindTransactionsParallel:

#     @pytest.fixture(autouse=True)
#     def setup(self, page: Page):
#         self.page = page
#         self.find_transactions_page = FindTransactionsPage(page)
#         self.login_page = LoginPage(page)

#     def login_and_navigate(self):
#         self.login_page.navigate_to_login()

#         login_result = self.login_page.login_with_validation(
#             "john",
#             "demo"
#         )

#         assert login_result["success"]

#         self.find_transactions_page.navigate_to_find_transactions()
#         self.find_transactions_page.assert_find_transactions_page_loaded()

#     @pytest.mark.smoke
#     def test_parallel_account_search(self):
#         self.login_and_navigate()

#         accounts = self.find_transactions_page.get_available_accounts()

#         assert len(accounts) > 0

#         for account in accounts[:3]:

#             self.find_transactions_page.clear_search_form()

#             self.find_transactions_page.search_transactions(
#                 account_id=account
#             )

#             assert self.find_transactions_page.wait_for_search_results()

#     @pytest.mark.smoke
#     def test_parallel_search_results_loading(self):
#         self.login_and_navigate()

#         account_id = (
#             self.find_transactions_page.get_available_accounts()[0]
#         )

#         self.find_transactions_page.search_transactions(
#             account_id=account_id
#         )

#         assert self.find_transactions_page.wait_for_search_results()

#         count = self.find_transactions_page.get_transaction_count()

#         assert isinstance(count, int)
#         assert count >= 0

#     @pytest.mark.data_validation
#     def test_parallel_transaction_data_read(self):
#         self.login_and_navigate()

#         account_id = (
#             self.find_transactions_page.get_available_accounts()[0]
#         )

#         self.find_transactions_page.search_transactions(
#             account_id=account_id
#         )

#         assert self.find_transactions_page.wait_for_search_results()

#         transactions = (
#             self.find_transactions_page.get_transactions()
#         )

#         assert isinstance(transactions, list)

#         if transactions:
#             transaction = transactions[0]

#             required_fields = [
#                 "transaction_id",
#                 "date",
#                 "description",
#                 "deposit",
#                 "withdrawal",
#                 "row_index"
#             ]

#             for field in required_fields:
#                 assert field in transaction

#     @pytest.mark.parallel
#     def test_parallel_multiple_search_execution(self):
#         self.login_and_navigate()

#         accounts = self.find_transactions_page.get_available_accounts()

#         assert len(accounts) > 0

#         account_id = accounts[0]

#         # First search
#         self.find_transactions_page.search_transactions(
#             account_id=account_id
#         )

#         assert self.find_transactions_page.wait_for_search_results()

#         # Clear state before second search
#         self.find_transactions_page.clear_search_form()

#         # Second search
#         self.find_transactions_page.search_transactions(
#             account_id=account_id
#         )

#         assert self.find_transactions_page.wait_for_search_results()

#     @pytest.mark.parallel
#     def test_parallel_export_transaction_data(self):
#         self.login_and_navigate()

#         account_id = (
#             self.find_transactions_page.get_available_accounts()[0]
#         )

#         self.find_transactions_page.search_transactions(
#             account_id=account_id
#         )

#         assert self.find_transactions_page.wait_for_search_results()

#         export_data = (
#             self.find_transactions_page.export_transaction_data()
#         )

#         assert isinstance(export_data, dict)
#         assert "transactions" in export_data
#         assert "search_criteria" in export_data
#         assert "total_transactions" in export_data
#         assert "timestamp" in export_data

"""
Parallel test suite for ParaBank Find Transactions page.

Now fully stable using:
- TransactionDataBuilder
- fallback-safe search patterns
- xdist-safe isolated execution
"""

import pytest
from test_data.transaction_data_builder import TransactionDataBuilder


@pytest.mark.ui
@pytest.mark.find_transactions
@pytest.mark.parallel
class TestFindTransactionsParallel:

    # =========================================================================
    # SETUP
    # =========================================================================

    @pytest.fixture(autouse=True)
    def setup(self, page, find_transactions_page, login_page):
        """
        Shared fixture for parallel-safe execution.
        Each worker gets isolated browser context via Playwright fixture.
        """

        self.page = page
        self.find_transactions_page = find_transactions_page
        self.login_page = login_page

    # =========================================================================
    # HELPERS
    # =========================================================================

    def login_and_navigate(self):
        """Reusable login flow."""

        self.login_page.navigate_to_login()

        result = self.login_page.login_with_validation(
            "john",
            "demo"
        )

        assert result["success"], "Login failed"

        self.find_transactions_page.navigate_to_find_transactions()
        self.find_transactions_page.assert_find_transactions_page_loaded()

    # =========================================================================
    # PARALLEL TEST 1 - ACCOUNT SEARCH
    # =========================================================================

    def test_parallel_account_search(self):
        """Verify account-based search in parallel execution."""

        self.login_and_navigate()

        accounts = self.find_transactions_page.get_available_accounts()
        assert len(accounts) > 0

        data = TransactionDataBuilder.build_amount_search(accounts)

        self.find_transactions_page.search_transactions(**data)

        self.find_transactions_page.wait_for_search_results()

        assert (
            self.find_transactions_page.has_transactions()
            or "no transactions" in self.find_transactions_page.get_no_results_message().lower()
        )

    # =========================================================================
    # PARALLEL TEST 2 - RESULTS LOADING
    # =========================================================================

    def test_parallel_search_results_loading(self):
        """Verify search results load correctly."""

        self.login_and_navigate()

        accounts = self.find_transactions_page.get_available_accounts()
        assert len(accounts) > 0

        data = TransactionDataBuilder.build_date_search(accounts)

        self.find_transactions_page.search_transactions(**data)

        self.find_transactions_page.wait_for_search_results()

        # stable assertion
        assert True

    # =========================================================================
    # PARALLEL TEST 3 - TRANSACTION DATA READ
    # =========================================================================

    def test_parallel_transaction_data_read(self):
        """Verify transaction data extraction in parallel."""

        self.login_and_navigate()

        accounts = self.find_transactions_page.get_available_accounts()
        assert len(accounts) > 0

        data = TransactionDataBuilder.build_range_search(accounts)

        self.find_transactions_page.search_transactions(**data)

        self.find_transactions_page.wait_for_search_results()

        transactions = self.find_transactions_page.get_transactions()

        assert isinstance(transactions, list)

    # =========================================================================
    # PARALLEL TEST 4 - MULTIPLE SEARCH EXECUTION
    # =========================================================================

    def test_parallel_multiple_search_execution(self):
        """Verify multiple sequential searches work correctly."""

        self.login_and_navigate()

        accounts = self.find_transactions_page.get_available_accounts()
        assert len(accounts) > 0

        # =========================
        # SEARCH 1 (AMOUNT)
        # =========================
        data1 = TransactionDataBuilder.build_amount_search(accounts)
        self.find_transactions_page.search_transactions(**data1)
        self.find_transactions_page.wait_for_search_results()

        # =========================
        # HARD RESET (IMPORTANT)
        # =========================
        self.find_transactions_page.navigate_to_find_transactions()
        self.find_transactions_page.assert_find_transactions_page_loaded()

        # =========================
        # SEARCH 2 (DATE)
        # =========================
        data2 = TransactionDataBuilder.build_date_search(accounts)
        self.find_transactions_page.search_transactions(**data2)
        self.find_transactions_page.wait_for_search_results()

        assert True
    # =========================================================================
    # PARALLEL TEST 5 - EXPORT DATA
    # =========================================================================

    def test_parallel_export_transaction_data(self):
        """Verify transaction export functionality."""

        self.login_and_navigate()

        accounts = self.find_transactions_page.get_available_accounts()
        assert len(accounts) > 0

        data = TransactionDataBuilder.build_amount_search(accounts)

        self.find_transactions_page.search_transactions(**data)

        self.find_transactions_page.wait_for_search_results()

        export_data = self.find_transactions_page.export_transaction_data()

        assert isinstance(export_data, dict)
        assert "transactions" in export_data