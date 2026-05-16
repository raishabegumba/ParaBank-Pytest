"""Comprehensive Pytest configuration and fixtures for UI tests."""
import pytest
import os
from datetime import datetime
from playwright.sync_api import Page, Browser, BrowserContext
from src.pages.base_page import BasePage
from src.pages.login_page import LoginPage
from src.pages.registration_page import RegistrationPage
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.pages.transfer_funds_page import TransferFundsPage
from src.pages.bill_pay_page import BillPayPage
from src.pages.open_account_page import OpenAccountPage
from src.pages.loan_request_page import LoanRequestPage
from src.pages.find_transactions_page import FindTransactionsPage
from src.utils.test_data_utils import TestDataUtils
from src.config.logger import log


@pytest.fixture(scope="session")
def test_environment():
    """Get test environment configuration."""
    return {
        'base_url': os.getenv('PARABANK_BASE_URL', 'http://localhost:8080/parabank'),
        'timeout': int(os.getenv('TEST_TIMEOUT', '30000')),
        'headless': os.getenv('HEADLESS', 'true').lower() == 'true',
        'slow_mo': int(os.getenv('SLOW_MO', '0')),
        'screenshot_on_failure': os.getenv('SCREENSHOT_ON_FAILURE', 'true').lower() == 'true',
        'video_on_failure': os.getenv('VIDEO_ON_FAILURE', 'false').lower() == 'true',
        'trace_on_failure': os.getenv('TRACE_ON_FAILURE', 'false').lower() == 'true',
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, test_environment):
    """Configure browser launch arguments."""
    launch_args = {
        'headless': test_environment['headless'],
        'slow_mo': test_environment['slow_mo'],
        'args': [
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--ignore-certificate-errors',
            '--ignore-ssl-errors',
            '--ignore-certificate-errors-spki-list',
        ]
    }
    return launch_args


@pytest.fixture
def page(page: Page, test_environment):
    """Configure page with test environment settings."""
    # Set default timeout
    page.set_default_timeout(test_environment['timeout'])
    
    # Set base URL for navigation (retry because ParaBank can be slow/flaky under load)
    if test_environment['base_url']:
        last_err = None
        for _ in range(3):
            try:
                page.goto(test_environment['base_url'], wait_until="domcontentloaded")
                last_err = None
                break
            except Exception as e:
                last_err = e
        if last_err is not None:
            raise last_err
    
    yield page
    
    # Cleanup after test
    page.close()



@pytest.fixture
def browser_context_args(browser_context_args, test_environment):
    """Configure browser context arguments."""
    context_args = {
        'viewport': {'width': 1920, 'height': 1080},
        'ignore_https_errors': True,
        'accept_downloads': True,
        'java_script_enabled': True,
    }
    
    # Add tracing if enabled
    if test_environment['trace_on_failure']:
        context_args['trace'] = 'on-first-retry'
    
    return context_args


@pytest.fixture
def base_page(page: Page):
    """Initialize base page object."""
    return BasePage(page)


@pytest.fixture
def login_page(page: Page):
    """Initialize login page object."""
    return LoginPage(page)


@pytest.fixture
def registration_page(page: Page):
    """Initialize registration page object."""
    return RegistrationPage(page)


@pytest.fixture
def accounts_overview_page(page: Page):
    """Initialize accounts overview page object."""
    return AccountsOverviewPage(page)


@pytest.fixture
def transfer_funds_page(page: Page):
    """Initialize transfer funds page object."""
    return TransferFundsPage(page)


@pytest.fixture
def bill_pay_page(page: Page):
    """Initialize bill pay page object."""
    return BillPayPage(page)


@pytest.fixture
def open_account_page(page: Page):
    """Initialize open account page object."""
    return OpenAccountPage(page)


@pytest.fixture
def loan_request_page(page: Page):
    """Initialize loan request page object."""
    return LoanRequestPage(page)


@pytest.fixture
def find_transactions_page(page: Page):
    """Initialize find transactions page object."""
    return FindTransactionsPage(page)


@pytest.fixture
def test_data():
    """Initialize test data utilities."""
    return TestDataUtils()


@pytest.fixture
def authenticated_user(page: Page, login_page: LoginPage, test_data: TestDataUtils):
    """Provide authenticated user session for tests."""
    # Get test user credentials
    test_user = test_data.get_test_user("raisha")
    
    # Perform login
    login_page.navigate_to_login()
    login_result = login_page.login_with_validation(
        test_user["username"], 
        test_user["password"]
    )
    
    assert login_result['success'], "Failed to authenticate test user"
    
    yield page
    
    # Logout after test
    try:
        accounts_overview = AccountsOverviewPage(page)
        accounts_overview.click_logout()
    except:
        # Ignore logout errors
        pass


@pytest.fixture
def multiple_test_users():
    """Provide multiple test user credentials for testing."""
    return [
        {'username': 'john', 'password': 'demo', 'role': 'user'},
        {'username': 'admin', 'password': 'admin', 'role': 'admin'},
    ]


@pytest.fixture
def test_scenarios():
    """Provide common test scenarios and data."""
    return {
        'valid_loan_amounts': ['1000.00', '5000.00', '10000.00'],
        'invalid_loan_amounts': ['0.00', '-100.00', 'abc', ''],
        'valid_transfer_amounts': ['10.00', '100.00', '1000.00'],
        'invalid_transfer_amounts': ['0.00', '-50.00', 'xyz', ''],
        'valid_dates': [
            datetime.now().strftime('%m/%d/%Y'),
            (datetime.now() - datetime.timedelta(days=30)).strftime('%m/%d/%Y'),
            (datetime.now() + datetime.timedelta(days=7)).strftime('%m/%d/%Y'),
        ],
        'invalid_dates': ['13/32/2023', '02/30/2023', 'invalid-date', ''],
    }


@pytest.fixture(autouse=True)
def test_setup_teardown(request, page: Page, test_environment):
    """Automatic test setup and teardown."""
    test_name = request.node.name
    log.info(f"Starting test: {test_name}")
    
    yield
    
    # Take screenshot on failure if enabled
    rep_call = getattr(request.node, "rep_call", None)
    if getattr(rep_call, "failed", False) and test_environment['screenshot_on_failure']:

        try:
            screenshot_path = f"screenshots/{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            os.makedirs('screenshots', exist_ok=True)
            page.screenshot(path=screenshot_path, full_page=True)
            log.info(f"Screenshot saved: {screenshot_path}")
        except Exception as e:
            log.warning(f"Failed to take screenshot: {e}")
    
    log.info(f"Completed test: {test_name}")


@pytest.fixture
def performance_monitor():
    """Monitor test performance metrics."""
    class PerformanceMonitor:
        def __init__(self):
            self.metrics = {}
            self.start_time = None
            self.end_time = None
        
        def start_timer(self, metric_name: str):
            self.start_time = datetime.now()
            self.current_metric = metric_name
        
        def end_timer(self):
            if self.start_time and self.current_metric:
                duration = (datetime.now() - self.start_time).total_seconds()
                self.metrics[self.current_metric] = duration
                self.start_time = None
                self.current_metric = None
                return duration
        
        def get_metric(self, metric_name: str):
            return self.metrics.get(metric_name, 0)
        
        def get_all_metrics(self):
            return self.metrics.copy()
    
    return PerformanceMonitor()


@pytest.fixture
def accessibility_validator():
    """Validate accessibility compliance."""
    class AccessibilityValidator:
        def __init__(self):
            self.issues = []
        
        def check_page_accessibility(self, page: Page):
            """Basic accessibility checks."""
            issues = []
            
            # Check for alt text on images
            images = page.locator('img')
            for i in range(images.count()):
                img = images.nth(i)
                alt_text = img.get_attribute('alt')
                if not alt_text or alt_text.strip() == '':
                    issues.append(f"Image {i} missing alt text")
            
            # Check for form labels
            inputs = page.locator('input[type="text"], input[type="password"], select, textarea')
            for i in range(inputs.count()):
                input_elem = inputs.nth(i)
                has_label = (
                    input_elem.get_attribute('aria-label') or
                    input_elem.get_attribute('placeholder') or
                    input_elem.locator('xpath=./preceding::label[1]').count() > 0
                )
                if not has_label:
                    input_id = input_elem.get_attribute('id')
                    issues.append(f"Input {input_id or i} missing label")
            
            self.issues = issues
            return issues
        
        def get_issues(self):
            return self.issues.copy()
        
        def clear_issues(self):
            self.issues = []
    
    return AccessibilityValidator()


@pytest.fixture
def data_generator():
    """Generate test data dynamically."""
    import random
    import string
    
    class DataGenerator:
        @staticmethod
        def random_string(length: int = 10) -> str:
            return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        
        @staticmethod
        def random_email() -> str:
            username = DataGenerator.random_string(8)
            domain = DataGenerator.random_string(6)
            return f"{username}@{domain}.com"
        
        @staticmethod
        def random_phone() -> str:
            return f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        @staticmethod
        def random_ssn() -> str:
            return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"
        
        @staticmethod
        def random_zip_code() -> str:
            return f"{random.randint(10000, 99999)}"
        
        @staticmethod
        def random_amount(min_val: float = 0.01, max_val: float = 9999.99) -> str:
            amount = random.uniform(min_val, max_val)
            return f"{amount:.2f}"
        
        @staticmethod
        def generate_test_user_data():
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            return {
                'first_name': f'Test{timestamp}',
                'last_name': f'User{timestamp}',
                'address': f'{random.randint(100, 999)} Test Street',
                'city': 'Test City',
                'state': 'CA',
                'zip_code': DataGenerator.random_zip_code(),
                'phone': DataGenerator.random_phone(),
                'ssn': DataGenerator.random_ssn(),
                'username': f'testuser_{timestamp}',
                'password': 'TestPass123!',
                'confirm_password': 'TestPass123!',
                'email': DataGenerator.random_email(),
            }
    
    return DataGenerator()


# Pytest hooks for enhanced reporting

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture per-phase report for later JSON artifact generation."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(autouse=True)
def _write_test_report_json(request, page: Page):
    """Write reports/html/test_report_<test>.json so HTML report can list PASS/FAIL.

    Note: This fixture must be robust even if the test fails early.
    """
    from src.config.settings import get_settings
    import json
    from pathlib import Path

    settings = get_settings()
    report_dir = Path(settings.html_report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    test_name = str(request.node.name)
    test_file = str(request.fspath)
    start_time = datetime.now().isoformat()

    yield

    # Prefer rep_call (set by pytest hooks) but fall back to phase reports.
    rep_call = getattr(request.node, "rep_call", None)
    if rep_call is None:
        rep_call = getattr(request.node, "rep_teardown", None) or getattr(request.node, "rep_setup", None)

    status = "passed"
    error_message = ""
    if rep_call is not None and getattr(rep_call, "failed", False):
        status = "failed"
        error_message = str(rep_call.longrepr) if getattr(rep_call, "longrepr", None) else "Unknown error"
    elif rep_call is not None and getattr(rep_call, "skipped", False):
        status = "skipped"
        error_message = str(rep_call.longrepr) if getattr(rep_call, "longrepr", None) else "Skipped"

    payload = {
        "test_name": test_name,
        "test_file": test_file,
        "status": status,
        "duration": (datetime.now() - datetime.fromisoformat(start_time)).total_seconds() if start_time else 0.0,
        "error_message": error_message,
        "start_time": start_time,
        "end_time": datetime.now().isoformat(),
        "metadata": {
            "markers": [m.name for m in request.node.iter_markers()],
            "node_id": request.node.nodeid,
        },
    }

    safe_name = test_name.replace('/', '_').replace(':', '_')
    out_path = report_dir / f"test_report_{safe_name}.json"
    out_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")




def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "smoke: mark test as smoke test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as regression test"
    )
    config.addinivalue_line(
        "markers", "ui: mark test as UI test"
    )
    config.addinivalue_line(
        "markers", "accessibility: mark test as accessibility test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security test"
    )
    config.addinivalue_line(
        "markers", "usability: mark test as usability test"
    )
    config.addinivalue_line(
        "markers", "navigation: mark test as navigation test"
    )
    config.addinivalue_line(
        "markers", "error_handling: mark test as error handling test"
    )
    config.addinivalue_line(
        "markers", "browser_compatibility: mark test as browser compatibility test"
    )
    config.addinivalue_line(
        "markers", "localization: mark test as localization test"
    )
    config.addinivalue_line(
        "markers", "responsive: mark test as responsive design test"
    )
    config.addinivalue_line(
        "markers", "edge_case: mark test as edge case test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "conditional: mark test as conditional test"
    )
    config.addinivalue_line(
        "markers", "business_rules: mark test as business rules test"
    )
    config.addinivalue_line(
        "markers", "data_validation: mark test as data validation test"
    )
    config.addinivalue_line(
        "markers", "data_filtering: mark test as data filtering test"
    )
    config.addinivalue_line(
        "markers", "advanced_search: mark test as advanced search test"
    )
    config.addinivalue_line(
        "markers", "data_export: mark test as data export test"
    )
    config.addinivalue_line(
        "markers", "data_analysis: mark test as data analysis test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add UI marker to all tests in ui directory
        if "ui" in str(item.fspath):
            item.add_marker(pytest.mark.ui)
        
        # Add smoke marker to basic functionality tests
        if "test_" in item.name and any(keyword in item.name for keyword in [
            "loads", "login", "registration", "transfer", "bill_pay", "open_account"
        ]):
            item.add_marker(pytest.mark.smoke)
        
        # Add regression marker to comprehensive tests
        if any(keyword in item.name for keyword in [
            "invalid", "error", "fail", "empty", "negative", "validation"
        ]):
            item.add_marker(pytest.mark.regression)
