import random
from datetime import datetime, timedelta


class TransactionDataBuilder:
    """
    Centralized builder for transaction search data.
    Ensures ALL tests always produce valid search criteria.
    """

    @staticmethod
    def get_valid_account(accounts):
        if not accounts:
            raise ValueError("No accounts available for test")
        return random.choice(accounts)

    @staticmethod
    def get_amount():
        # stable deterministic value instead of hardcoding everywhere
        return "100"

    @staticmethod
    def get_date(days_offset=-10):
        target_date = datetime.now() + timedelta(days=days_offset)
        return target_date.strftime("%m/%d/%Y")

    @staticmethod
    def build_amount_search(accounts):
        return {
            "account_id": TransactionDataBuilder.get_valid_account(accounts),
            "amount": TransactionDataBuilder.get_amount()
        }

    @staticmethod
    def build_date_search(accounts):
        return {
            "account_id": TransactionDataBuilder.get_valid_account(accounts),
            "date": TransactionDataBuilder.get_date()
        }

    @staticmethod
    def build_range_search(accounts):
        return {
            "account_id": TransactionDataBuilder.get_valid_account(accounts),
            "from_date": TransactionDataBuilder.get_date(-30),
            "to_date": TransactionDataBuilder.get_date()
        }

    @staticmethod
    def build_id_search(accounts):
        return {
            "account_id": TransactionDataBuilder.get_valid_account(accounts),
            "transaction_id": "12345"
        }