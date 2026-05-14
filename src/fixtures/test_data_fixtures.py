"""Enterprise-grade test data fixtures for comprehensive testing."""
import pytest
import json
import random
from typing import Generator, Dict, Any, List
from faker import Faker
from pathlib import Path
from src.config.settings import get_settings
from src.config.logger import log


# Provide `fake_data` as a fixture (some tests depend on this exact name).
@pytest.fixture(scope="session")
def fake_data() -> Faker:
    """Faker instance for generating test data."""
    return Faker()




@pytest.fixture(scope="session")
def user_test_data(fake_data: Faker) -> Dict[str, Any]:

    """
    User test data fixture.
    
    Args:
        fake_data: Faker instance
        
    Returns:
        Dictionary with user test data
    """
    return {
        'valid_user': {
            'username': 'john.doe',
            'password': 'Password123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'address': '123 Main Street',
            'city': 'New York',
            'state': 'NY',
            'zip_code': '10001',
            'phone': '555-123-4567',
            'ssn': '123-45-6789'
        },
        'invalid_user': {
            'username': 'invalid.user',
            'password': 'WrongPassword123!',
            'first_name': 'Invalid',
            'last_name': 'User',
            'address': '456 Invalid Street',
            'city': 'Invalid City',
            'state': 'XX',
            'zip_code': '00000',
            'phone': '000-000-0000',
            'ssn': '000-00-0000'
        },
        'random_users': [
            {
                'username': fake_data.user_name(),
                'password': fake_data.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True),
                'first_name': fake_data.first_name(),
                'last_name': fake_data.last_name(),
                'address': fake_data.street_address(),
                'city': fake_data.city(),
                'state': fake_data.state_abbr(),
                'zip_code': fake_data.zipcode(),
                'phone': fake_data.phone_number(),
                'ssn': fake_data.ssn()
            }
            for _ in range(5)
        ]
    }


@pytest.fixture(scope="session")
def account_test_data() -> Dict[str, Any]:
    """
    Account test data fixture.
    
    Returns:
        Dictionary with account test data
    """
    return {
        'checking_account': {
            'type': 'CHECKING',
            'initial_deposit': '1000.00',
            'description': 'Initial checking account deposit'
        },
        'savings_account': {
            'type': 'SAVINGS',
            'initial_deposit': '5000.00',
            'description': 'Initial savings account deposit'
        },
        'account_types': ['CHECKING', 'SAVINGS'],
        'invalid_amounts': ['-100', '0', 'abc', '1.234.56', ''],
        'valid_amounts': ['1', '10.50', '100', '1000.00', '9999.99']
    }


@pytest.fixture(scope="session")
def transaction_test_data() -> Dict[str, Any]:
    """
    Transaction test data fixture.
    
    Returns:
        Dictionary with transaction test data
    """
    return {
        'transfer_amounts': ['10', '50', '100', '500', '1000'],
        'bill_pay_amounts': ['25', '50', '100', '250', '500'],
        'descriptions': [
            'Transfer to savings',
            'Monthly rent payment',
            'Grocery shopping',
            'Utility bill payment',
            'Restaurant dinner'
        ],
        'transaction_types': ['DEBIT', 'CREDIT', 'ALL'],
        'invalid_amounts': ['-50', '0', 'abc', '1.23.45'],
        'large_amounts': ['10000', '50000', '100000'],
        'date_ranges': {
            'today': '12/12/2024',
            'this_week': '12/08/2024',
            'this_month': '12/01/2024',
            'last_month': '11/01/2024'
        }
    }


@pytest.fixture(scope="session")
def loan_test_data() -> Dict[str, Any]:
    """
    Loan test data fixture.
    
    Returns:
        Dictionary with loan test data
    """
    return {
        'small_loan': {
            'amount': '5000',
            'down_payment': '500',
            'description': 'Small personal loan'
        },
        'medium_loan': {
            'amount': '25000',
            'down_payment': '5000',
            'description': 'Medium personal loan'
        },
        'large_loan': {
            'amount': '100000',
            'down_payment': '20000',
            'description': 'Large personal loan'
        },
        'invalid_loans': [
            {'amount': '500', 'down_payment': '50'},  # Too small
            {'amount': '-1000', 'down_payment': '100'},  # Negative
            {'amount': 'abc', 'down_payment': '100'},  # Invalid format
            {'amount': '10000', 'down_payment': '15000'},  # Down payment > loan
        ],
        'down_payment_percentages': [5, 10, 20, 30, 50],
        'loan_amounts': ['1000', '5000', '10000', '25000', '50000', '100000']
    }


@pytest.fixture(scope="session")
def payee_test_data(fake_data: Faker) -> Dict[str, Any]:
    """
    Payee test data fixture.
    
    Args:
        fake_data: Faker instance
        
    Returns:
        Dictionary with payee test data
    """
    return {
        'utility_payee': {
            'name': 'Electric Company',
            'address': '123 Power Street',
            'city': 'Energy City',
            'state': 'EC',
            'zip_code': '12345',
            'phone': '555-POWER-1',
            'account_number': 'ELEC-12345'
        },
        'insurance_payee': {
            'name': 'Health Insurance Co',
            'address': '456 Insurance Ave',
            'city': 'Coverage Town',
            'state': 'CT',
            'zip_code': '67890',
            'phone': '555-HEALTH-1',
            'account_number': 'HLTH-67890'
        },
        'random_payees': [
            {
                'name': fake_data.company(),
                'address': fake_data.street_address(),
                'city': fake_data.city(),
                'state': fake_data.state_abbr(),
                'zip_code': fake_data.zipcode(),
                'phone': fake_data.phone_number(),
                'account_number': f"ACC-{random.randint(10000, 99999)}"
            }
            for _ in range(3)
        ]
    }


# NOTE:
# Some tests import `security_test_data` and `boundary_test_data` as plain data
# (not as pytest fixtures) and then subscript them, e.g. security_test_data['xss_payloads'].
# To support both usage patterns, we provide these as module-level data dicts,
# not as fixtures.

security_test_data: Dict[str, Any] = {
    'xss_payloads': [
        '<script>alert("XSS")</script>',
        '"><script>alert("XSS")</script>',
        '<img src=x onerror=alert("XSS")>',
        'javascript:alert("XSS")',
        '<svg onload=alert("XSS")>'
    ],
    'sql_injection_payloads': [
        "' OR '1'='1",
        "' OR 1=1--",
        "'; DROP TABLE users;--",
        "' UNION SELECT * FROM users--",
        "admin'--"
    ],
    'invalid_usernames': [
        'admin',
        'administrator',
        'root',
        'test',
        'guest',
        '<script>alert("XSS")</script>',
        "' OR '1'='1"
    ],
    'weak_passwords': [
        'password',
        '123456',
        'admin',
        'qwerty',
        'letmein',
        'password123'
    ],
    'brute_force_attempts': [
        'user1', 'user2', 'user3', 'test1', 'test2',
        'admin1', 'admin2', 'john', 'jane', 'user'
    ]
}


@pytest.fixture(scope="session")
def security_test_data_fixture() -> Dict[str, Any]:
    """Pytest fixture wrapper for compatibility with fixture-based tests."""
    return security_test_data


@pytest.fixture(scope="session")
def performance_test_data() -> Dict[str, Any]:

    """
    Performance test data fixture.
    
    Returns:
        Dictionary with performance test data
    """
    return {
        'thresholds': {
            'page_load': 3.0,      # seconds
            'api_response': 1.0,    # seconds
            'form_submission': 2.0,  # seconds
            'search_results': 1.5    # seconds
        },
        'load_patterns': {
            'light': {'users': 1, 'duration': 60},
            'medium': {'users': 10, 'duration': 300},
            'heavy': {'users': 100, 'duration': 600}
        },
        'endpoints': [
            '/index.htm',
            '/overview.htm',
            '/transfer.htm',
            '/billpay.htm',
            '/findtrans.htm'
        ]
    }


@pytest.fixture(scope="function")
def dynamic_test_data(fake_data: Faker) -> Dict[str, Any]:
    """
    Dynamic test data fixture for each test function.
    
    Args:
        fake_data: Faker instance
        
    Returns:
        Dictionary with dynamic test data
    """
    return {
        'username': fake_data.user_name(),
        'password': fake_data.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True),
        'first_name': fake_data.first_name(),
        'last_name': fake_data.last_name(),
        'email': fake_data.email(),
        'phone': fake_data.phone_number(),
        'address': fake_data.street_address(),
        'city': fake_data.city(),
        'state': fake_data.state_abbr(),
        'zip_code': fake_data.zipcode(),
        'amount': str(random.randint(1, 1000)),
        'description': fake_data.sentence(),
        'company': fake_data.company(),
        'account_number': f"ACC-{random.randint(10000, 99999)}"
    }


@pytest.fixture(scope="session")
def test_data_manager():
    """
    Test data manager fixture for managing test data lifecycle.
    
    Returns:
        TestDataManager instance
    """
    class TestDataManager:
        def __init__(self):
            self.generated_data = {}
            self.used_data = set()
            self.settings = get_settings()
            self.data_dir = Path(self.settings.test_data_dir)
            self.data_dir.mkdir(exist_ok=True)
        
        def generate_unique_username(self, base_name: str = "testuser") -> str:
            """Generate unique username."""
            counter = 1
            while True:
                username = f"{base_name}{counter}"
                if username not in self.used_data:
                    self.used_data.add(username)
                    return username
                counter += 1
        
        def save_test_data(self, data: Dict[str, Any], filename: str) -> None:
            """Save test data to file."""
            filepath = self.data_dir / f"{filename}.json"
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            log.info(f"Test data saved to {filepath}")
        
        def load_test_data(self, filename: str) -> Dict[str, Any]:
            """Load test data from file."""
            filepath = self.data_dir / f"{filename}.json"
            if filepath.exists():
                with open(filepath, 'r') as f:
                    return json.load(f)
            return {}
        
        def cleanup_test_data(self) -> None:
            """Clean up generated test data."""
            if self.settings.cleanup_test_data:
                # Clean up temporary files
                for file in self.data_dir.glob("temp_*.json"):
                    file.unlink()
                log.info("Test data cleanup completed")
    
    return TestDataManager()


@pytest.fixture(scope="function")
def environment_test_data(get_settings) -> Dict[str, Any]:
    """
    Environment-specific test data fixture.
    
    Args:
        get_settings: Settings getter
        
    Returns:
        Dictionary with environment-specific data
    """
    settings = get_settings()
    
    base_data = {
        'base_url': settings.base_url,
        'test_username': settings.test_username,
        'test_password': settings.test_password,
        'browser': settings.browser.value,
        'headless': settings.headless
    }
    
    # Environment-specific overrides
    if settings.test_env.value == 'dev':
        base_data.update({
            'timeout_multiplier': 2.0,
            'retry_attempts': 3,
            'debug_mode': True
        })
    elif settings.test_env.value == 'staging':
        base_data.update({
            'timeout_multiplier': 1.5,
            'retry_attempts': 2,
            'debug_mode': False
        })
    elif settings.test_env.value == 'prod':
        base_data.update({
            'timeout_multiplier': 1.0,
            'retry_attempts': 1,
            'debug_mode': False
        })
    
    return base_data




boundary_test_data: Dict[str, Any] = {
    'amount_boundaries': {
        'minimum': '0.01',
        'maximum': '999999.99',
        # Backwards-compatible keys expected by existing tests
        'invalid_minimum': '0',
        'invalid_maximum': '1000000.00',
        'invalid_amounts': ['0', '-1', 'abc', '1000000.00', ''],
        'decimal_limits': ['0.1', '0.01', '0.001', '999999.999']
    },

        'text_boundaries': {
            'min_length': 1,
            'max_length': 255,
            'empty': '',
            'max_length_plus_one': 'a' * 256,
            'special_chars': '!@#$%^&*()_+-=[]{}|;:,.<>?',
            'unicode': '测试🚀🌟'
        },
        'date_boundaries': {
            'min_date': '01/01/1900',
            'max_date': '12/31/2099',
            'invalid_dates': ['13/01/2024', '02/30/2024', '00/00/0000', 'abc']
        }
    }
