"""Utility functions for test data handling."""
import json
from pathlib import Path
from faker import Faker
from src.config.logger import log

fake = Faker()


class TestDataUtils:
    """Test data utilities class for managing test data."""
    
    def __init__(self):
        """Initialize test data utilities."""
        self.test_data_cache = {}
    
    def get_test_user(self, username: str) -> dict:
        """Get test user credentials."""
        # Default test users
        test_users = {
            "raisha": {"username": "raisha", "password": "Password@1234"},
            "admin": {"username": "admin", "password": "admin"}
        }
        return test_users.get(username, {"username": "testuser", "password": "testpass"})
    
    def load_test_data(self, filename: str) -> dict:
        """Load test data from JSON file."""
        try:
            file_path = Path(f"test_data/{filename}.json")
            with open(file_path, "r") as f:
                data = json.load(f)
            log.info(f"Loaded test data from {filename}")
            return data
        except FileNotFoundError:
            log.error(f"Test data file not found: {filename}")
            raise
    
    def save_test_data(self, filename: str, data: dict):
        """Save test data to JSON file."""
        try:
            file_path = Path(f"test_data/{filename}.json")
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            log.info(f"Saved test data to {filename}")
        except Exception as e:
            log.error(f"Failed to save test data: {e}")
            raise
    
    def generate_random_user(self):
        """Generate random user data using Faker."""
        return {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "address": fake.address(),
            "username": fake.user_name(),
            "password": fake.password(length=12, special_chars=True),
        }
    
    def generate_random_email(self):
        """Generate random email."""
        return fake.email()
    
    def generate_random_phone(self):
        """Generate random phone number."""
        return fake.phone_number()
    
    def generate_random_address(self):
        """Generate random address."""
        return fake.address()


def load_test_data(filename: str) -> dict:
    """Load test data from JSON file."""
    try:
        file_path = Path(f"test_data/{filename}.json")
        with open(file_path, "r") as f:
            data = json.load(f)
        log.info(f"Loaded test data from {filename}")
        return data
    except FileNotFoundError:
        log.error(f"Test data file not found: {filename}")
        raise


def save_test_data(filename: str, data: dict):
    """Save test data to JSON file."""
    try:
        file_path = Path(f"test_data/{filename}.json")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        log.info(f"Saved test data to {filename}")
    except Exception as e:
        log.error(f"Failed to save test data: {e}")
        raise


def generate_random_user():
    """Generate random user data using Faker."""
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "address": fake.address(),
        "username": fake.user_name(),
        "password": fake.password(length=12, special_chars=True),
    }


def generate_random_email():
    """Generate random email."""
    return fake.email()


def generate_random_phone():
    """Generate random phone number."""
    return fake.phone_number()


def generate_random_address():
    """Generate random address."""
    return fake.address()
