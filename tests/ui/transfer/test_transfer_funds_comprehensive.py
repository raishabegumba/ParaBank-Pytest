"""Unique comprehensive transfer funds tests not covered in test_transfer_funds.py."""

import pytest
from playwright.sync_api import Page

from src.config.logger import log
from src.pages.transfer_funds_page import TransferFundsPage


@pytest.mark.ui
@pytest.mark.transfer
class TestTransferFundsComprehensive:
    """Unique comprehensive transfer funds tests."""

    @pytest.fixture(autouse=True)
    def setup(self, authenticated_user: Page):
        self.page = authenticated_user
        self.transfer_page = TransferFundsPage(self.page)
        self.transfer_page.navigate_to_transfer_funds()

    def get_valid_accounts(self):
        """Get valid distinct from/to accounts."""
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()

        if len(from_accounts) < 2:
            pytest.skip("Need at least 2 accounts for transfer tests")

        from_account = from_accounts[0]
        to_account = next(
            acc for acc in to_accounts if acc != from_account
        )

        return from_account, to_account

    @pytest.mark.positive
    def test_valid_transfer(self):
        """Test valid fund transfer between accounts."""
        from_account, to_account = self.get_valid_accounts()
        amount = "100.00"

        self.transfer_page.perform_transfer(
            from_account,
            to_account,
            amount
        )

        assert self.transfer_page.is_transfer_successful()

        log.info(f"Valid transfer test passed: {amount}")

    @pytest.mark.negative
    def test_invalid_amount_format(self):
        """Test transfer rejects non-numeric amount."""
        from_account, to_account = self.get_valid_accounts()

        self.transfer_page.select_from_account(from_account)
        self.transfer_page.select_to_account(to_account)
        self.transfer_page.enter_amount("abc")

        self.transfer_page.click_transfer_button()

        assert not self.transfer_page.is_transfer_successful()

        log.info("Invalid amount format validation passed")

    @pytest.mark.positive
    def test_transfer_confirmation_contains_amount(self):
        """Test transfer confirmation displays transferred amount."""
        from_account, to_account = self.get_valid_accounts()
        amount = "50.00"

        self.transfer_page.perform_transfer(
            from_account,
            to_account,
            amount
        )

        assert self.transfer_page.is_transfer_successful()

        confirmation = (
            self.transfer_page.get_transfer_confirmation_details()
        )

        assert confirmation.get("amount")
        assert amount in confirmation["amount"]

        log.info("Transfer confirmation amount validation passed")

    @pytest.mark.positive
    def test_transfer_limits_validation(self):
        """Test transfer limits and business rules."""
        validation = self.transfer_page.validate_transfer_limits(
            100.00
        )

        assert validation["within_transaction_limit"]
        assert validation["within_daily_limit"]

        log.info("Transfer limits validation passed")

    @pytest.mark.performance
    def test_transfer_performance(self, performance_monitor):
        """Test transfer performance."""
        from_account, to_account = self.get_valid_accounts()

        performance_monitor.start_timer("transfer")

        self.transfer_page.perform_transfer(
            from_account,
            to_account,
            "100.00"
        )

        transfer_complete = (
            self.transfer_page.wait_for_transfer_complete()
        )

        performance_monitor.end_timer()

        assert transfer_complete

        duration = performance_monitor.get_metric("transfer")

        assert duration < 5.0, (
            f"Transfer took {duration:.2f}s"
        )

        log.info(
            f"Transfer performance passed: {duration:.2f}s"
        )

    @pytest.mark.regression
    def test_transfer_with_validation_simulation(self):
        """Test transfer with comprehensive validation simulation."""
        from_account, to_account = self.get_valid_accounts()

        result = (
            self.transfer_page.simulate_transfer_with_validation(
                from_account,
                to_account,
                "100.00"
            )
        )

        assert isinstance(result, dict)
        assert "success" in result
        assert "validation_results" in result

        if result["success"]:
            assert "confirmation_details" in result

        log.info(
            f"Transfer simulation passed: {result['success']}"
        )

    @pytest.mark.boundary
    def test_large_amount_transfer(self):
        """Test transfer with large amount."""
        from_account, to_account = self.get_valid_accounts()

        self.transfer_page.perform_transfer(
            from_account,
            to_account,
            "9999.99"
        )

        transfer_complete = (
            self.transfer_page.wait_for_transfer_complete()
        )

        assert transfer_complete

        log.info("Large amount transfer passed")

    @pytest.mark.navigation
    def test_navigation_to_accounts_overview(self):
        """Test navigation back to accounts overview."""
        self.transfer_page.click_accounts_overview()

        assert "overview" in self.page.url

        log.info(
            "Navigation to accounts overview passed"
        )