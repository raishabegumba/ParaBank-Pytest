"""Comprehensive transfer funds page tests covering all scenarios."""
import pytest
from playwright.sync_api import Page
from src.pages.transfer_funds_page import TransferFundsPage
from src.pages.login_page import LoginPage
from src.utils.wait_helpers import WaitStrategy
from src.fixtures.test_data_fixtures import user_test_data, transaction_test_data, boundary_test_data
from src.config.settings import get_settings
from src.config.logger import log


@pytest.mark.ui
@pytest.mark.transfer
@pytest.mark.smoke
class TestTransferFundsComprehensive:
    """Comprehensive transfer funds test suite."""
    
    @pytest.fixture(autouse=True)
    def setup(self, authenticated_page: Page):
        """Setup authenticated test instance."""
        self.page = authenticated_page
        self.transfer_page = TransferFundsPage(self.page)
        self.transfer_page.navigate_to_transfer_funds()
    
    @pytest.mark.positive
    def test_valid_transfer(self, transaction_test_data):
        """Test valid fund transfer between accounts."""
        # Arrange
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        
        if len(from_accounts) < 2:
            pytest.skip("Need at least 2 accounts for transfer test")
        
        from_account = from_accounts[0]
        to_account = [acc for acc in to_accounts if acc != from_account][0]
        amount = transaction_test_data['transfer_amounts'][0]  # Use first valid amount
        
        # Act
        self.transfer_page.perform_transfer(from_account, to_account, amount)
        
        # Assert
        self.transfer_page.assert_transfer_successful()
        assert self.transfer_page.is_transfer_successful()
        
        log.info(f"Valid transfer test passed: {amount} from {from_account} to {to_account}")
    
    @pytest.mark.negative
    @pytest.mark.parametrize("scenario", [
        {"from": "", "to": "12345", "amount": "100", "expected_error": "From account is required"},
        {"from": "12345", "to": "", "amount": "100", "expected_error": "To account is required"},
        {"from": "12345", "to": "12345", "amount": "100", "expected_error": "From and To accounts must be different"},
        {"from": "12345", "to": "67890", "amount": "", "expected_error": "Amount is required"},
        {"from": "12345", "to": "67890", "amount": "0", "expected_error": "Amount must be greater than 0"},
        {"from": "12345", "to": "67890", "amount": "-100", "expected_error": "Amount must be greater than 0"},
        {"from": "12345", "to": "67890", "amount": "abc", "expected_error": "Amount must be a valid number"}
    ])
    def test_invalid_transfer_scenarios(self, scenario):
        """Test various invalid transfer scenarios."""
        # Act
        if scenario['from']:
            self.transfer_page.select_from_account(scenario['from'])
        if scenario['to']:
            self.transfer_page.select_to_account(scenario['to'])
        if scenario['amount']:
            self.transfer_page.enter_amount(scenario['amount'])
        
        self.transfer_page.click_transfer_button()
        
        # Assert
        if 'expected_error' in scenario:
            self.transfer_page.assert_transfer_failed(scenario['expected_error'])
        else:
            self.transfer_page.assert_transfer_failed()
        
        assert not self.transfer_page.is_transfer_successful()
        
        log.info(f"Invalid transfer test passed for scenario: {scenario}")
    
    @pytest.mark.negative
    @pytest.mark.parametrize("amount", boundary_test_data['amount_boundaries']['invalid_amounts'])
    def test_invalid_amounts(self, amount):
        """Test transfer with invalid amount formats."""
        # Arrange
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        
        if len(from_accounts) < 2:
            pytest.skip("Need at least 2 accounts for transfer test")
        
        from_account = from_accounts[0]
        to_account = [acc for acc in to_accounts if acc != from_account][0]
        
        # Act
        self.transfer_page.perform_transfer(from_account, to_account, amount)
        
        # Assert
        self.transfer_page.assert_transfer_failed()
        assert not self.transfer_page.is_transfer_successful()
        
        log.info(f"Invalid amount test passed for: {amount}")
    
    @pytest.mark.positive
    def test_transfer_with_description(self, transaction_test_data):
        """Test transfer with description."""
        # Arrange
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        
        if len(from_accounts) < 2:
            pytest.skip("Need at least 2 accounts for transfer test")
        
        from_account = from_accounts[0]
        to_account = [acc for acc in to_accounts if acc != from_account][0]
        amount = transaction_test_data['transfer_amounts'][1]
        description = transaction_test_data['descriptions'][0]
        
        # Act
        self.transfer_page.perform_transfer(from_account, to_account, amount, description)
        
        # Assert
        self.transfer_page.assert_transfer_successful()
        
        # Check confirmation details
        confirmation = self.transfer_page.get_transfer_confirmation_details()
        assert confirmation.get('amount', '').replace('$', '') == amount, \
            "Amount should match in confirmation"
        
        log.info(f"Transfer with description test passed: {description}")
    
    @pytest.mark.positive
    def test_transfer_limits_validation(self, transaction_test_data):
        """Test transfer limits and business rules."""
        # Arrange
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        
        if len(from_accounts) < 2:
            pytest.skip("Need at least 2 accounts for transfer test")
        
        from_account = from_accounts[0]
        to_account = [acc for acc in to_accounts if acc != from_account][0]
        
        # Test valid amount
        valid_amount = transaction_test_data['transfer_amounts'][2]
        validation = self.transfer_page.validate_transfer_limits(float(valid_amount))
        
        # Assert
        assert validation['within_transaction_limit'], "Valid amount should be within transaction limit"
        assert validation['within_daily_limit'], "Valid amount should be within daily limit"
        assert validation['sufficient_funds'], "Should have sufficient funds for valid amount"
        
        log.info("Transfer limits validation test passed")
    
    @pytest.mark.ui
    def test_transfer_form_validation(self):
        """Test transfer form validation states."""
        # Act
        validation_state = self.transfer_page.validate_transfer_form()
        
        # Assert
        assert isinstance(validation_state, dict), "Should return validation state dictionary"
        
        expected_keys = [
            'from_account_selected', 'to_account_selected', 'amount_entered',
            'valid_amount', 'different_accounts', 'form_ready', 'issues'
        ]
        assert all(key in validation_state for key in expected_keys), \
            "Should contain all validation keys"
        
        # Initial state should not be ready
        assert not validation_state['form_ready'], "Empty form should not be ready"
        
        log.info("Transfer form validation test passed")
    
    @pytest.mark.ui
    def test_account_selection_functionality(self):
        """Test account selection functionality."""
        # Act
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        
        # Assert
        assert isinstance(from_accounts, list), "Should return list of from accounts"
        assert isinstance(to_accounts, list), "Should return list of to accounts"
        assert len(from_accounts) > 0, "Should have at least one from account"
        assert len(to_accounts) > 0, "Should have at least one to account"
        
        log.info(f"Account selection test passed - From: {len(from_accounts)}, To: {len(to_accounts)}")
    
    @pytest.mark.performance
    def test_transfer_performance(self, performance_metrics):
        """Test transfer performance."""
        # Arrange
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        
        if len(from_accounts) < 2:
            pytest.skip("Need at least 2 accounts for transfer test")
        
        from_account = from_accounts[0]
        to_account = [acc for acc in to_accounts if acc != from_account][0]
        amount = "100"
        
        # Act
        performance_metrics.start_timer("transfer")
        self.transfer_page.perform_transfer(from_account, to_account, amount)
        transfer_complete = self.transfer_page.wait_for_transfer_complete()
        performance_metrics.end_timer("transfer")
        
        # Assert
        assert transfer_complete, "Transfer should complete within timeout"
        
        # Check performance
        transfer_duration = performance_metrics.get_average("transfer")
        assert transfer_duration < 5.0, f"Transfer took {transfer_duration}s, should be under 5s"
        
        log.info(f"Transfer performance test passed: {transfer_duration:.2f}s")
    
    @pytest.mark.ui
    def test_transfer_confirmation_details(self):
        """Test transfer confirmation details accuracy."""
        # Arrange
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        
        if len(from_accounts) < 2:
            pytest.skip("Need at least 2 accounts for transfer test")
        
        from_account = from_accounts[0]
        to_account = [acc for acc in to_accounts if acc != from_account][0]
        amount = "250.50"
        description = "Test transfer confirmation"
        
        # Act
        self.transfer_page.perform_transfer(from_account, to_account, amount, description)
        
        # Wait for success
        transfer_complete = self.transfer_page.wait_for_transfer_complete()
        assert transfer_complete, "Transfer should complete"
        
        # Assert
        confirmation = self.transfer_page.get_transfer_confirmation_details()
        assert isinstance(confirmation, dict), "Should return confirmation dictionary"
        
        if confirmation.get('amount'):
            assert amount in confirmation['amount'], "Amount should match in confirmation"
        
        log.info(f"Transfer confirmation test passed: {confirmation}")
    
    @pytest.mark.ui
    def test_clear_transfer_form(self):
        """Test clearing transfer form."""
        # Arrange
        from_accounts = self.transfer_page.get_from_accounts()
        
        if not from_accounts:
            pytest.skip("No accounts available for testing")
        
        # Fill form with data
        self.transfer_page.select_from_account(from_accounts[0])
        self.transfer_page.enter_amount("100")
        self.transfer_page.enter_description("Test description")
        
        # Act
        self.transfer_page.clear_transfer_form()
        
        # Assert
        validation_state = self.transfer_page.validate_transfer_form()
        assert not validation_state['amount_entered'], "Amount should be cleared"
        
        log.info("Clear transfer form test passed")
    
    @pytest.mark.ui
    def test_navigation_to_accounts_overview(self):
        """Test navigation back to accounts overview."""
        # Act
        self.transfer_page.click_accounts_overview()
        
        # Assert
        current_url = self.transfer_page.get_url()
        assert "overview" in current_url, "Should navigate to accounts overview"
        
        log.info("Navigation to accounts overview test passed")
    
    @pytest.mark.regression
    def test_transfer_with_validation_simulation(self, transaction_test_data):
        """Test transfer with comprehensive validation simulation."""
        # Arrange
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        
        if len(from_accounts) < 2:
            pytest.skip("Need at least 2 accounts for transfer test")
        
        from_account = from_accounts[0]
        to_account = [acc for acc in to_accounts if acc != from_account][0]
        amount = transaction_test_data['transfer_amounts'][0]
        
        # Act
        result = self.transfer_page.simulate_transfer_with_validation(
            from_account, to_account, amount
        )
        
        # Assert
        assert isinstance(result, dict), "Should return result dictionary"
        assert 'success' in result, "Should contain success flag"
        assert 'validation_results' in result, "Should contain validation results"
        
        if result['success']:
            assert 'confirmation_details' in result, "Should contain confirmation details"
        
        log.info(f"Transfer simulation test passed: {result['success']}")
    
    @pytest.mark.boundary
    def test_large_amount_transfer(self, transaction_test_data):
        """Test transfer with large amounts."""
        # Arrange
        from_accounts = self.transfer_page.get_from_accounts()
        to_accounts = self.transfer_page.get_to_accounts()
        
        if len(from_accounts) < 2:
            pytest.skip("Need at least 2 accounts for transfer test")
        
        from_account = from_accounts[0]
        to_account = [acc for acc in to_accounts if acc != from_account][0]
        large_amount = transaction_test_data['large_amounts'][0]  # Use first large amount
        
        # Act
        self.transfer_page.perform_transfer(from_account, to_account, large_amount)
        
        # Assert - Should either succeed or show appropriate error
        transfer_complete = self.transfer_page.wait_for_transfer_complete()
        assert transfer_complete, "Large amount transfer should complete (success or error)"
        
        log.info(f"Large amount transfer test passed for: {large_amount}")
    
    @pytest.mark.ui
    def test_transfer_page_loaded(self):
        """Test transfer funds page loads correctly."""
        # Assert
        self.transfer_page.assert_transfer_page_loaded()
        
        log.info("Transfer page load test passed")


@pytest.mark.ui
@pytest.mark.transfer
@pytest.mark.parallel
class TestTransferFundsParallel:
    """Parallel transfer funds tests for performance testing."""
    
    def test_parallel_transfer_performance(self, authenticated_page: Page, performance_metrics):
        """Test transfer performance under parallel execution."""
        # Setup
        transfer_page = TransferFundsPage(authenticated_page)
        transfer_page.navigate_to_transfer_funds()
        
        # Arrange
        from_accounts = transfer_page.get_from_accounts()
        to_accounts = transfer_page.get_to_accounts()
        
        if len(from_accounts) < 2:
            pytest.skip("Need at least 2 accounts for transfer test")
        
        from_account = from_accounts[0]
        to_account = [acc for acc in to_accounts if acc != from_account][0]
        
        # Act
        performance_metrics.start_timer("parallel_transfer")
        transfer_page.perform_transfer(from_account, to_account, "50")
        transfer_complete = transfer_page.wait_for_transfer_complete()
        performance_metrics.end_timer("parallel_transfer")
        
        # Assert
        assert transfer_complete, "Parallel transfer should complete"
        
        log.info("Parallel transfer performance test passed")


@pytest.mark.ui
@pytest.mark.transfer
@pytest.mark.mobile
class TestTransferFundsMobile:
    """Mobile-specific transfer funds tests."""
    
    def test_mobile_transfer_responsive(self, mobile_page: Page):
        """Test transfer on mobile viewport."""
        # Setup - Login and navigate
        login_page = LoginPage(mobile_page)
        login_page.navigate_to_login()
        login_page.login("john.doe", "Password123!")
        
        transfer_page = TransferFundsPage(mobile_page)
        transfer_page.navigate_to_transfer_funds()
        
        # Arrange
        from_accounts = transfer_page.get_from_accounts()
        to_accounts = transfer_page.get_to_accounts()
        
        if len(from_accounts) < 2:
            pytest.skip("Need at least 2 accounts for transfer test")
        
        from_account = from_accounts[0]
        to_account = [acc for acc in to_accounts if acc != from_account][0]
        
        # Act
        transfer_page.perform_transfer(from_account, to_account, "25")
        
        # Assert
        transfer_complete = transfer_page.wait_for_transfer_complete()
        assert transfer_complete, "Mobile transfer should complete"
        
        log.info("Mobile transfer test passed")
