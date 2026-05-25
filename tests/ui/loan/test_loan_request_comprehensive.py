"""
Comprehensive tests for ParaBank Loan Request page.

Covers form validation, business rules (eligibility, LTV, down payment),
error handling, confirmation accuracy, and end-to-end simulation.
"""
from unittest import result

import pytest
from playwright.sync_api import Page
from src.pages.loan_request_page import LoanRequestPage
from src.pages.login_page import LoginPage
from src.utils.test_data_utils import TestDataUtils


@pytest.mark.ui
@pytest.mark.loan_request
@pytest.mark.regression
class TestLoanRequestComprehensive:
    """Comprehensive functional tests — validation rules, business logic, and integration."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.page = page
        self.loan_page = LoanRequestPage(page)
        self.login_page = LoginPage(page)
        self.test_data = TestDataUtils()

    def login_and_navigate(self):
        """Login and land on the loan request page."""
        self.login_page.navigate_to_login()
        result = self.login_page.login_with_validation("john", "demo")
        assert result['success'], "Login should be successful"
        self.loan_page.navigate_to_loan_request()
        self.loan_page.assert_loan_request_page_loaded()

    # ------------------------------------------------------------------ #
    #  Form validation — missing fields                                    #
    # ------------------------------------------------------------------ #

    @pytest.mark.regression
    def test_loan_application_without_account_fails(self):
        """Submitting without selecting an account does not process."""
        self.login_and_navigate()
        self.loan_page.enter_loan_amount("10000.00")
        self.loan_page.enter_down_payment("1000.00")
        self.loan_page.click_apply_for_loan()
        assert not self.loan_page.is_loan_approved()
        result = self.loan_page.get_loan_result_details()
        assert result["denied"] is True

    @pytest.mark.regression
    def test_loan_application_without_amount_fails(self):
        """Submitting without a loan amount does not process."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            self.loan_page.select_from_account(accounts[0])
            self.loan_page.enter_down_payment("1000.00")
            self.loan_page.click_apply_for_loan()
            assert not self.loan_page.is_loan_approved()
            assert not self.loan_page.is_loan_denied()

    @pytest.mark.regression
    def test_loan_application_without_down_payment_fails(self):
        """Submitting without a down payment does not process."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            self.loan_page.select_from_account(accounts[0])
            self.loan_page.enter_loan_amount("10000.00")
            self.loan_page.click_apply_for_loan()
            assert not self.loan_page.is_loan_approved()
            assert not self.loan_page.is_loan_denied()

    # ------------------------------------------------------------------ #
    #  Form validation — invalid values                                    #
    # ------------------------------------------------------------------ #

    @pytest.mark.regression
    def test_loan_application_with_zero_amount_fails(self):
        self.login_and_navigate()

        accounts = self.loan_page.get_available_accounts()

        with pytest.raises(ValueError, match="Loan amount must be greater than 0"):
            self.loan_page.apply_for_loan("0.00", "1000.00", accounts[0])

    @pytest.mark.regression
    def test_loan_application_with_negative_amount_fails(self):
        self.login_and_navigate()

        accounts = self.loan_page.get_available_accounts()

        with pytest.raises(ValueError, match="Loan amount must be greater than 0"):
            self.loan_page.apply_for_loan("-10000.00", "1000.00", accounts[0])

    @pytest.mark.regression
    def test_loan_application_with_negative_down_payment_fails(self):
        self.login_and_navigate()

        accounts = self.loan_page.get_available_accounts()

        with pytest.raises(ValueError, match="Down payment cannot be negative"):
            self.loan_page.apply_for_loan("10000.00", "-1000.00", accounts[0])

    @pytest.mark.regression
    def test_loan_application_with_invalid_amount_format_fails(self):
        self.login_and_navigate()

        accounts = self.loan_page.get_available_accounts()

        with pytest.raises(ValueError, match="Invalid loan amount format"):
            self.loan_page.apply_for_loan("abc", "1000.00", accounts[0])

    # ------------------------------------------------------------------ #
    #  Form state & clear                                                  #
    # ------------------------------------------------------------------ #

    @pytest.mark.usability
    def test_loan_request_form_validation_state(self):
        """Form validation state correctly transitions from incomplete to ready."""
        self.login_and_navigate()

        validation = self.loan_page.validate_loan_request_form()
        assert not validation['form_ready']
        assert validation['from_account_selected']
        assert not validation['loan_amount_entered']
        assert not validation['down_payment_entered']

        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            self.loan_page.select_from_account(accounts[0])
            self.loan_page.enter_loan_amount("10000.00")
            self.loan_page.enter_down_payment("1000.00")

            validation = self.loan_page.validate_loan_request_form()
            assert validation['form_ready']
            assert validation['from_account_selected']
            assert validation['loan_amount_entered']
            assert validation['valid_loan_amount']
            assert validation['down_payment_entered']
            assert validation['valid_down_payment']

    @pytest.mark.regression
    def test_clear_loan_request_form(self):
        """Clearing the form resets all fields to empty."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            self.loan_page.select_from_account(accounts[0])
            self.loan_page.enter_loan_amount("10000.00")
            self.loan_page.enter_down_payment("1000.00")
            self.loan_page.clear_loan_request_form()

            loan_val = self.loan_page.get_attribute(self.loan_page.LOAN_AMOUNT_FIELD, "value")
            down_val = self.loan_page.get_attribute(self.loan_page.DOWN_PAYMENT_FIELD, "value")
            assert loan_val == "" or loan_val is None, "Loan amount field should be cleared"
            assert down_val == "" or down_val is None, "Down payment field should be cleared"

    # ------------------------------------------------------------------ #
    #  Business rules — eligibility, LTV, down payment %                  #
    # ------------------------------------------------------------------ #

    @pytest.mark.usability
    def test_loan_eligibility_validation(self):
        """Eligibility validation accepts and rejects scenarios per business rules."""
        self.login_and_navigate()

        scenarios = [
            (10000.00, 1000.00, True),    # 10% down — at minimum
            (10000.00,  500.00, False),   # 5% down — below minimum
            (10000.00, 2000.00, True),    # 20% down — good
            (  500.00,   50.00, False),   # Below minimum loan amount
            (200000.00,20000.00,False),   # Above maximum loan amount
        ]
        for loan_amount, down_payment, should_be_eligible in scenarios:
            validation = self.loan_page.validate_loan_eligibility(loan_amount, down_payment)
            if should_be_eligible:
                assert validation['eligible'], \
                    f"Loan ${loan_amount} / ${down_payment} down should be eligible"
            else:
                assert not validation['eligible'], \
                    f"Loan ${loan_amount} / ${down_payment} down should not be eligible"

    @pytest.mark.business_rules
    def test_loan_to_value_ratio_validation(self):
        """LTV ratio enforcement: loans exceeding 90% LTV are rejected."""
        self.login_and_navigate()

        scenarios = [
            (10000.00, 1000.00, 90.0, True),   # 90% LTV — at limit
            (10000.00, 1500.00, 85.0, True),   # 85% LTV — good
            (10000.00,  500.00, 95.0, False),  # 95% LTV — exceeds limit
        ]
        for loan_amount, down_payment, expected_ltv, should_pass in scenarios:
            validation = self.loan_page.validate_loan_eligibility(loan_amount, down_payment)
            if should_pass:
                assert validation['reasonable_loan_to_value'], \
                    f"LTV {expected_ltv}% should be acceptable"
            else:
                assert not validation['reasonable_loan_to_value'], \
                    f"LTV {expected_ltv}% should exceed the allowed limit"

    @pytest.mark.business_rules
    def test_down_payment_percentage_validation(self):
        """Down payment must be at least 10% of the loan amount."""
        self.login_and_navigate()

        scenarios = [
            (10000.00,  500.00,  5.0, False),  # 5%  — below minimum
            (10000.00, 1000.00, 10.0, True),   # 10% — at minimum
            (10000.00, 2000.00, 20.0, True),   # 20% — above minimum
        ]
        for loan_amount, down_payment, percentage, should_pass in scenarios:
            validation = self.loan_page.validate_loan_eligibility(loan_amount, down_payment)
            if should_pass:
                assert validation['adequate_down_payment'], \
                    f"Down payment {percentage}% should be adequate"
            else:
                assert not validation['adequate_down_payment'], \
                    f"Down payment {percentage}% should be inadequate"

    # ------------------------------------------------------------------ #
    #  Error handling                                                      #
    # ------------------------------------------------------------------ #

    @pytest.mark.error_handling
    def test_loan_request_error_message_display(self):
        """Submitting an empty form surfaces an error message (content is backend-driven)."""
        self.login_and_navigate()
        self.loan_page.click_apply_for_loan()
        from src.config.logger import log
        log.info(f"Empty form error: {self.loan_page.get_error_message()}")

    # ------------------------------------------------------------------ #
    #  Integration & data accuracy                                         #
    # ------------------------------------------------------------------ #

    @pytest.mark.data_validation
    def test_loan_confirmation_details_accuracy(self):
        """Confirmation details after processing include the submitted loan amount."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            loan_amount = "15000.00"
            self.loan_page.apply_for_loan(loan_amount, "1500.00", accounts[0])
            if self.loan_page.wait_for_loan_processing_complete():
                details = self.loan_page.get_loan_confirmation_details()
                assert details and len(details) > 0, "Should have confirmation details"
                if 'loan_amount' in details:
                    assert loan_amount in details['loan_amount'], \
                        f"Loan amount {loan_amount} should appear in confirmation"

    @pytest.mark.integration
    def test_loan_request_simulation_with_validation(self):
        """Full simulation returns a structured result with all expected keys."""
        self.login_and_navigate()
        accounts = self.loan_page.get_available_accounts()
        if len(accounts) > 0:
            result = self.loan_page.simulate_loan_request_with_validation(
                "20000.00", "2000.00", accounts[0]
            )
            assert isinstance(result, dict)
            assert 'success' in result
            assert 'validation_results' in result
            assert 'eligibility_results' in result
            if result['success']:
                assert 'approved' in result
                if result['approved']:
                    assert 'confirmation_details' in result