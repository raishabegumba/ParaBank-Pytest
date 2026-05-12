# ParaBank Enterprise Test Framework Guide

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Running Tests](#running-tests)
6. [Test Organization](#test-organization)
7. [Page Object Model](#page-object-model)
8. [Advanced Features](#advanced-features)
9. [Reporting](#reporting)
10. [CI/CD Integration](#cicd-integration)
11. [Security Testing](#security-testing)
12. [Best Practices](#best-practices)
13. [Troubleshooting](#troubleshooting)

## Overview

The ParaBank Enterprise Test Framework is a comprehensive, production-grade automation testing framework built with Playwright, Python, and Pytest. It provides enterprise-grade features including:

- **Page Object Model (POM)** design pattern
- **Advanced wait strategies** and synchronization
- **Retry mechanisms** with exponential backoff
- **Comprehensive reporting** (Allure, HTML, screenshots)
- **Security testing** capabilities
- **CI/CD integration** (GitHub Actions, Jenkins)
- **Parallel execution** support
- **Environment management**
- **Data-driven and config-driven testing**

### Key Features

- ✅ **Enterprise Architecture**: Scalable, maintainable, modular design
- ✅ **Advanced Utilities**: Wait helpers, retry handlers, screenshot management
- ✅ **Comprehensive Coverage**: UI, API, security, performance testing
- ✅ **Rich Reporting**: Allure, HTML dashboards, detailed test reports
- ✅ **CI/CD Ready**: GitHub Actions and Jenkins pipelines
- ✅ **Security Focused**: XSS, SQL injection, CSRF, path traversal scanning
- ✅ **Performance Optimized**: Parallel execution, performance metrics
- ✅ **Production Quality**: Error handling, logging, retry mechanisms

## Architecture

### Framework Structure

```
parabank-pytest/
├── src/
│   ├── config/                 # Configuration management
│   │   ├── settings.py         # Enhanced settings with Pydantic
│   │   └── logger.py           # Loguru-based logging
│   ├── pages/                  # Page Object Model
│   │   ├── base_page.py        # Base page with common utilities
│   │   ├── login_page.py       # Login page object
│   │   ├── registration_page.py # Registration page object
│   │   ├── accounts_overview_page.py # Accounts overview
│   │   ├── transfer_funds_page.py    # Transfer funds
│   │   ├── bill_pay_page.py          # Bill payment
│   │   ├── find_transactions_page.py  # Transaction search
│   │   ├── open_account_page.py       # Account opening
│   │   └── loan_request_page.py       # Loan requests
│   ├── utils/                  # Utility classes
│   │   ├── wait_helpers.py     # Advanced wait strategies
│   │   ├── retry_handler.py    # Retry with backoff & circuit breaker
│   │   ├── screenshot_manager.py # Screenshot management
│   │   ├── assertion_helpers.py # Rich assertion helpers
│   │   └── webdriver_utils.py  # Browser utilities
│   ├── fixtures/               # Test fixtures
│   │   ├── browser_fixtures.py # Browser management
│   │   ├── test_data_fixtures.py # Test data generation
│   │   └── reporting_fixtures.py # Reporting fixtures
│   ├── reporting/              # Reporting system
│   │   ├── allure_reporter.py  # Allure integration
│   │   ├── html_reporter.py    # HTML dashboard
│   │   └── report_manager.py   # Centralized reporting
│   └── security/               # Security testing
│       └── security_scanner.py # Comprehensive security scanner
├── tests/                      # Test suites
│   ├── ui/                     # UI tests
│   │   ├── test_login_comprehensive.py
│   │   ├── test_registration_comprehensive.py
│   │   ├── test_accounts_overview_comprehensive.py
│   │   ├── test_transfer_funds_comprehensive.py
│   │   ├── test_security_comprehensive.py
│   │   └── test_end_to_end_workflows.py
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── conftest.py            # Pytest configuration
├── docker/                     # Docker configurations
├── .github/workflows/          # GitHub Actions
├── jenkins/                    # Jenkins configuration
├── docs/                       # Documentation
├── reports/                    # Generated reports
└── requirements.txt            # Dependencies
```

### Design Patterns

1. **Page Object Model (POM)**: Separates page interactions from test logic
2. **Factory Pattern**: For browser and context creation
3. **Strategy Pattern**: For different wait strategies
4. **Observer Pattern**: For reporting and monitoring
5. **Builder Pattern**: For test data generation

## Installation & Setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose
- Git

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd parabank-pytest
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright Browsers**
   ```bash
   python -m playwright install chromium firefox webkit
   python -m playwright install-deps
   ```

5. **Setup Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Start ParaBank Application**
   ```bash
   docker-compose -f docker/docker-compose.test.yml up -d
   ```

7. **Verify Installation**
   ```bash
   pytest tests/ui/test_login_comprehensive.py::TestLoginComprehensive::test_valid_login -v
   ```

## Configuration

### Environment Configuration

The framework uses Pydantic for type-safe configuration. Main configuration is in `src/config/settings.py`:

```python
from pydantic import BaseSettings
from enum import Enum

class Environment(Enum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"

class Browser(Enum):
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"

class Settings(BaseSettings):
    # Application Settings
    base_url: str = "http://localhost:8080"
    api_base_url: str = "http://localhost:8080/parabank/services"
    
    # Browser Configuration
    browser: Browser = Browser.CHROMIUM
    headless: bool = True
    window_width: int = 1920
    window_height: int = 1080
    
    # Timeouts
    implicit_wait: int = 10000
    explicit_wait: int = 30000
    navigation_timeout: int = 60000
    
    # Test Configuration
    test_env: Environment = Environment.DEV
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
```

### Environment Variables

Create `.env` file:

```env
# Application URLs
BASE_URL=http://localhost:8080
API_BASE_URL=http://localhost:8080/parabank/services

# Browser Configuration
BROWSER=chromium
HEADLESS=true
WINDOW_WIDTH=1920
WINDOW_HEIGHT=1080

# Timeouts (milliseconds)
IMPLICIT_WAIT=10000
EXPLICIT_WAIT=30000
NAVIGATION_TIMEOUT=60000

# Test Configuration
TEST_ENV=dev
LOG_LEVEL=INFO

# Test Credentials
TEST_USERNAME=john.doe
TEST_PASSWORD=Password123!

# Reporting
SCREENSHOT_ON_FAILURE=true
VIDEO_RECORDING=true
TRACE_RECORDING=true

# Performance
PARALLEL_WORKERS=4
RETRY_MAX_ATTEMPTS=3
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/ui/test_login_comprehensive.py

# Run specific test method
pytest tests/ui/test_login_comprehensive.py::TestLoginComprehensive::test_valid_login

# Run with verbose output
pytest -v

# Run with specific markers
pytest -m smoke
pytest -m regression
pytest -m security
```

### Advanced Test Execution

```bash
# Run tests in parallel
pytest -n 4

# Run with HTML report
pytest --html=reports/test-report.html --self-contained-html

# Run with Allure report
pytest --alluredir=allure-results

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Run with performance profiling
pytest --benchmark-only

# Run with retry on failure
pytest --retry=3

# Run with timeout
pytest --timeout=300
```

### Browser Selection

```bash
# Run with specific browser
pytest --browser=chromium
pytest --browser=firefox
pytest --browser=webkit

# Run headed (non-headless)
pytest --headed

# Run with specific viewport
pytest --viewport=1280x720
```

### Environment-Specific Execution

```bash
# Run for different environments
TEST_ENV=staging pytest
TEST_ENV=prod pytest

# Or use configuration files
pytest --env-config=config/staging.yaml
```

## Test Organization

### Test Markers

The framework uses pytest markers for test categorization:

```python
@pytest.mark.smoke        # Critical path tests
@pytest.mark.regression   # Full regression suite
@pytest.mark.security     # Security tests
@pytest.mark.performance  # Performance tests
@pytest.mark.ui          # UI tests
@pytest.mark.api         # API tests
@pytest.mark.mobile      # Mobile-specific tests
@pytest.mark.parallel     # Parallel execution
@pytest.mark.e2e         # End-to-end tests
```

### Test Structure

```python
@pytest.mark.ui
@pytest.mark.login
@pytest.mark.smoke
class TestLoginComprehensive:
    """Comprehensive login page test suite."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test instance."""
        self.login_page = LoginPage(page)
        self.login_page.navigate_to_login()
    
    @pytest.mark.positive
    def test_valid_login(self, user_test_data):
        """Test login with valid credentials."""
        # Test implementation
        pass
    
    @pytest.mark.negative
    @pytest.mark.parametrize("username,password,expected_error", [
        ("invalid", "password", "The username and password could not be verified"),
        ("", "password", "Please enter a username and password"),
    ])
    def test_invalid_login_scenarios(self, username, password, expected_error):
        """Test various invalid login scenarios."""
        # Test implementation
        pass
```

### Data-Driven Testing

```python
@pytest.mark.parametrize("test_data", [
    {"username": "user1", "password": "pass1", "expected": "success"},
    {"username": "user2", "password": "pass2", "expected": "failure"},
])
def test_data_driven_login(self, test_data):
    """Data-driven login test."""
    # Test implementation using test_data
    pass
```

## Page Object Model

### Base Page

All page objects inherit from `BasePage`:

```python
from src.pages.base_page import BasePage

class LoginPage(BasePage):
    """Enterprise-grade Login page object for ParaBank."""
    
    # Locators
    USERNAME_FIELD = "#username"
    PASSWORD_FIELD = "#password"
    LOGIN_BUTTON = "input[type='submit'][value='Log In']"
    
    def __init__(self, page: Page):
        """Initialize Login page with enterprise features."""
        super().__init__(page)
        self.wait_helper = WaitHelper(page)
        self.assert_helper = AssertionHelper(page)
    
    def login(self, username: str, password: str) -> None:
        """Perform complete login action with validation."""
        try:
            self.enter_username(username)
            self.enter_password(password)
            self.click_login()
            log.info(f"Login attempted for user: {username}")
        except Exception as e:
            log.error(f"Login failed: {e}")
            raise
```

### Advanced Features

Page objects include enterprise features:

- **Wait Strategies**: Multiple wait strategies with custom conditions
- **Retry Mechanisms**: Automatic retry with exponential backoff
- **Assertions**: Rich assertion helpers with detailed error messages
- **Logging**: Comprehensive logging for debugging
- **Screenshots**: Automatic screenshot capture on failures

## Advanced Features

### Wait Strategies

```python
from src.utils.wait_helpers import WaitHelper, WaitStrategy

wait_helper = WaitHelper(page)

# Different wait strategies
wait_helper.wait_for_element(selector, WaitStrategy.ELEMENT_VISIBLE)
wait_helper.wait_for_element(selector, WaitStrategy.ELEMENT_CLICKABLE)
wait_helper.wait_for_element(selector, WaitStrategy.ELEMENT_PRESENT)
wait_helper.wait_for_element(selector, WaitStrategy.ELEMENT_HIDDEN)

# Custom wait conditions
wait_helper.wait_for_custom_condition(
    condition=lambda: page.is_visible("#success-message"),
    timeout=10000,
    message="Success message not appeared"
)
```

### Retry Mechanisms

```python
from src.utils.retry_handler import retry_with_backoff

@retry_with_backoff(max_attempts=3, base_delay=0.5)
def navigate_to_login(self):
    """Navigate to login page with retry mechanism."""
    self.goto(f"{self.page.context.browser._browser_options.base_url}/index.htm")
    self.assert_helper.assert_element_visible(self.USERNAME_FIELD)
```

### Screenshot Management

```python
from src.utils.screenshot_manager import ScreenshotManager

screenshot_manager = ScreenshotManager(page)

# Take screenshot
screenshot_path = screenshot_manager.take_screenshot("login_page")

# Take failure screenshot
failure_screenshot = screenshot_manager.take_failure_screenshot(
    test_name="test_login", 
    error_message="Login failed"
)

# Create screenshot gallery
gallery_path = screenshot_manager.create_screenshot_gallery("test_session")
```

### Assertion Helpers

```python
from src.utils.assertion_helpers import AssertionHelper

assert_helper = AssertionHelper(page)

# Rich assertions
assert_helper.assert_element_visible(selector)
assert_helper.assert_element_contains_text(selector, expected_text)
assert_helper.assert_element_enabled(selector)
assert_helper.assert_element_clickable(selector)

# Custom assertions
assert_helper.assert_with_retry(
    condition=lambda: page.is_visible("#success-message"),
    message="Success message should be visible"
)
```

## Reporting

### Allure Reporting

```python
from src.reporting.allure_reporter import get_allure_reporter

# Get reporter instance
reporter = get_allure_reporter(page)

# Start test reporting
reporter.start_test("Login Test", "login_001")
reporter.add_test_epic("Authentication")
reporter.add_test_feature("Login")
reporter.add_test_severity("critical")

# Attach artifacts
reporter.attach_screenshot("login_page")
reporter.attach_json_data(test_data, "Test Data")

# Mark test result
reporter.mark_test_passed("Login successful")
```

### HTML Reporting

```python
from src.reporting.html_reporter import get_html_reporter

# Get HTML reporter
html_reporter = get_html_reporter()

# Add test result
test_result = {
    'test_name': 'Login Test',
    'status': 'passed',
    'duration': 2.5,
    'screenshots': ['/path/to/screenshot.png']
}
html_reporter.add_test_result(test_result)

# Generate reports
reports = html_reporter.generate_all_reports()
```

### Centralized Reporting

```python
from src.reporting.report_manager import get_report_manager

# Setup comprehensive reporting
manager = get_report_manager(page)
manager.start_test_reporting(
    test_name="Login Test",
    test_id="login_001",
    epic="Authentication",
    feature="Login",
    severity="critical"
)

# Attach artifacts
manager.attach_screenshot("login_page")
manager.attach_performance_metrics({'login_time': 2.5})

# Mark test result
manager.mark_test_passed("Login successful")

# Generate all reports
reports = manager.finalize_session()
```

## CI/CD Integration

### GitHub Actions

The framework includes a comprehensive GitHub Actions workflow (`.github/workflows/ci-cd.yml`):

**Features:**
- Multi-browser testing
- Parallel execution
- Security scanning
- Performance testing
- Automated reporting
- Deployment pipelines

**Usage:**
1. Push to trigger builds
2. Pull requests for testing
3. Manual dispatch with parameters
4. Scheduled nightly runs

### Jenkins

Jenkins configuration (`jenkins/Jenkinsfile`):

**Features:**
- Parameterized builds
- Parallel test execution
- Docker integration
- Comprehensive reporting
- Deployment stages

**Usage:**
1. Configure Jenkins with the provided Jenkinsfile
2. Set up required parameters
3. Run builds with different test types

### Docker Integration

```bash
# Start test environment
docker-compose -f docker/docker-compose.test.yml up -d

# Run tests against Docker environment
pytest --base-url=http://localhost:8080

# Stop environment
docker-compose -f docker/docker-compose.test.yml down
```

## Security Testing

### Security Scanner

```python
from src.security.security_scanner import SecurityScanner

# Initialize scanner
scanner = SecurityScanner(page)

# Run comprehensive security scan
scan_results = scanner.run_comprehensive_security_scan("http://localhost:8080")

# Generate security report
report_html = scanner.generate_security_report(scan_results)

# Save report
with open("security_report.html", "w") as f:
    f.write(report_html)
```

### Security Tests

The framework includes comprehensive security tests:

- **XSS Protection**: Cross-site scripting vulnerability scanning
- **SQL Injection**: SQL injection vulnerability detection
- **Path Traversal**: Directory traversal vulnerability testing
- **CSRF Protection**: Cross-site request forgery validation
- **Security Headers**: Missing security header detection

### Running Security Tests

```bash
# Run all security tests
pytest -m security

# Run specific security scan
pytest tests/ui/test_security_comprehensive.py

# Generate security report
pytest -m security --security-report
```

## Best Practices

### Test Design

1. **Page Object Model**: Separate page interactions from test logic
2. **Single Responsibility**: Each test should test one thing
3. **Data Independence**: Tests should not depend on each other
4. **Clear Assertions**: Use descriptive assertion messages
5. **Error Handling**: Handle exceptions gracefully

### Code Quality

1. **Type Hints**: Use Python type hints
2. **Documentation**: Document all public methods
3. **Error Messages**: Provide clear error messages
4. **Logging**: Log important actions and decisions
5. **Code Reviews**: Review code for quality and security

### Performance

1. **Parallel Execution**: Use parallel execution for faster runs
2. **Smart Waits**: Use appropriate wait strategies
3. **Resource Cleanup**: Clean up resources after tests
4. **Retry Logic**: Implement retry for flaky tests
5. **Batch Operations**: Batch similar operations

### Security

1. **Credential Management**: Never hardcode credentials
2. **Input Validation**: Validate all user inputs
3. **Error Handling**: Don't expose sensitive information
4. **Secure Reporting**: Sanitize reports before sharing
5. **Regular Scanning**: Run regular security scans

## Troubleshooting

### Common Issues

1. **Browser Not Found**
   ```bash
   python -m playwright install chromium firefox webkit
   python -m playwright install-deps
   ```

2. **Docker Issues**
   ```bash
   docker-compose down
   docker system prune -f
   docker-compose up -d
   ```

3. **Import Errors**
   ```bash
   pip install -r requirements.txt
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
   ```

4. **Timeout Issues**
   ```bash
   # Increase timeouts in configuration
   EXPLICIT_WAIT=60000 pytest
   ```

### Debug Mode

```bash
# Run with debug logging
LOG_LEVEL=DEBUG pytest

# Run headed for visual debugging
pytest --headed

# Run with browser devtools
pytest --browser=chromium --headed --devtools
```

### Performance Issues

```bash
# Run with fewer parallel workers
pytest -n 2

# Run with timeout disabled
pytest --timeout=0

# Run specific test only
pytest tests/ui/test_login_comprehensive.py::TestLoginComprehensive::test_valid_login
```

### Reporting Issues

```bash
# Clean old reports
rm -rf reports/ allure-results/

# Generate fresh reports
pytest --alluredir=allure-results --html=reports/test-report.html

# View Allure report
allure serve allure-results
```

## Support

For issues and questions:

1. Check the logs in `logs/` directory
2. Review generated reports in `reports/` directory
3. Check the troubleshooting section above
4. Review test code for proper implementation
5. Verify configuration settings

---

**Framework Version**: 1.0.0  
**Last Updated**: 2024-12-12  
**Maintainer**: ParaBank QA Team
