"""Sample API client for ParaBank API."""
from src.api.base_api import BaseAPI


class ParaBankAPI(BaseAPI):
    """ParaBank API client."""

    def __init__(self, base_url: str = None):
        """Initialize ParaBank API client."""
        super().__init__(base_url)

    # Customers endpoints
    def get_customers(self):
        """Get all customers."""
        return self.get("/customers")

    def get_customer(self, customer_id: int):
        """Get customer by ID."""
        return self.get(f"/customers/{customer_id}")

    def create_customer(self, data: dict):
        """Create new customer."""
        return self.post("/customers", json=data)

    def update_customer(self, customer_id: int, data: dict):
        """Update customer."""
        return self.put(f"/customers/{customer_id}", json=data)

    def delete_customer(self, customer_id: int):
        """Delete customer."""
        return self.delete(f"/customers/{customer_id}")

    # Accounts endpoints
    def get_accounts(self):
        """Get all accounts."""
        return self.get("/accounts")

    def get_account(self, account_id: int):
        """Get account by ID."""
        return self.get(f"/accounts/{account_id}")

    def get_account_transactions(self, account_id: int):
        """Get account transactions."""
        return self.get(f"/accounts/{account_id}/transactions")
