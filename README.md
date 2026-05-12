"""README - ParaBank PyTest Framework"""

# ParaBank PyTest Framework

An industry-standard PyTest automation framework for testing the ParaBank application.

## Project Structure

```
ParaBank-Pytest/
├── src/
│   ├── config/              # Configuration management
│   │   ├── settings.py      # Application settings
│   │   └── logger.py        # Logging configuration
│   ├── pages/               # Page Object Models for UI tests
│   │   └── base_page.py     # Base page class with common methods
│   ├── api/                 # API client and utilities
│   │   └── base_api.py      # Base API client class
│   └── utils/               # Utility functions
│       ├── webdriver_utils.py   # Selenium utilities
│       └── test_data_utils.py   # Test data utilities
├── tests/
│   ├── ui/                  # UI test cases
│   │   ├── test_login.py    # Login page tests
│   │   └── conftest.py      # UI test fixtures
│   ├── api/                 # API test cases
│   │   ├── test_api.py      # API endpoint tests
│   │   └── conftest.py      # API test fixtures
│   ├── performance/         # Performance tests
│   ├── conftest.py          # Main pytest configuration
│   └── __init__.py
├── test_data/               # Test data files (JSON)
├── reports/                 # Test reports directory
├── logs/                    # Log files directory
├── .github/workflows/       # CI/CD pipeline configurations
├── pytest.ini               # PyTest configuration
├── pyproject.toml           # Project metadata
├── requirements.txt         # Python dependencies
├── requirements-dev.txt     # Development dependencies
├── .env.example             # Environment variables example
└── README.md                # This file
```

## Prerequisites

- Python 3.9 or higher
- pip package manager
- Playwright browsers (auto-installed)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ParaBank-Pytest
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/ui/test_login.py
```

### Run Tests by Marker
```bash
pytest -m smoke                 # Run smoke tests
pytest -m regression            # Run regression tests
pytest -m ui                    # Run UI tests
pytest -m api                   # Run API tests
```

### Run Tests with Options
```bash
pytest -v                       # Verbose output
pytest -s                       # Show print statements
pytest -x                       # Stop on first failure
pytest --maxfail=3              # Stop after 3 failures
pytest --tb=short               # Short traceback format
```

### Generate HTML Report
```bash
pytest --html=reports/report.html --self-contained-html
```

### Generate Coverage Report
```bash
pytest --cov=src --cov-report=html
```

### Run Tests in Parallel
```bash
pytest -n auto                  # Use auto-detected number of CPUs
pytest -n 4                     # Use 4 processes
```

## Key Features

### 1. Page Object Model (POM)
- Organized page objects for maintainability
- Base page class with reusable Playwright methods
- Clear separation of page selectors and actions
- Supports CSS selectors and Playwright locator strategies

### 2. Configuration Management
- Environment-based configuration using Pydantic
- Environment variables support
- Centralized settings management

### 3. Logging
- Structured logging using loguru
- Separate console and file logging
- DEBUG and INFO level support

### 4. Fixtures
- Session, function, and module-scoped fixtures
- Automatic Playwright page initialization and cleanup
- API client fixtures

### 5. Test Data Management
- JSON-based test data
- Random data generation using Faker
- Test data utilities

### 6. Test Organization
- Smoke tests for critical paths
- Regression tests for comprehensive coverage
- Performance tests
- API and UI test separation

### 7. Reporting
- HTML report generation
- Failure screenshots
- Log files for debugging
- Coverage reports

## Writing Tests

### UI Test Example
```python
@pytest.mark.ui
@pytest.mark.smoke
class TestLoginPage:
    @pytest.fixture(autouse=True)
    def setup(self, page):
        self.page = BasePage(page)
    
    def test_login_success(self):
        self.page.fill("#username", "testuser")
        self.page.click("#login_btn")
        self.page.page.wait_for_load_state("networkidle")
        assert "dashboard" in self.page.get_url()
```

### API Test Example
```python
@pytest.mark.api
@pytest.mark.smoke
class TestCustomersAPI:
    def test_get_customers(self, api_client):
        response = api_client.get("/customers")
        assert response.status_code == 200
        assert len(response.json()) > 0
```

## Configuration

### Pytest Configuration (pytest.ini)
- Test discovery patterns
- Markers for test categorization
- Logging configuration
- Report format

### Environment Variables (.env)
- Application URLs
- Browser settings
- Selenium timeouts
- Test credentials

## CI/CD Integration

Place CI/CD workflow files in `.github/workflows/` for GitHub Actions integration.

### Example workflow structure:
- Trigger on push/pull requests
- Run tests across multiple Python versions
- Generate reports
- Upload artifacts

## Best Practices

1. **Use Page Object Model** - Keep page selectors separate from test logic
2. **Meaningful Test Names** - Test names should describe what is being tested
3. **Use Markers** - Categorize tests with pytest markers
4. **DRY Principle** - Use fixtures and base classes to avoid duplication
5. **Explicit Waits** - Use Playwright's built-in waits instead of sleep
6. **Logging** - Log important steps for debugging
7. **Data Isolation** - Use test data generators to avoid conflicts
8. **Cleanup** - Ensure proper teardown in fixtures

## Troubleshooting

### Playwright Browser Issues
- Install Playwright browsers: `playwright install`
- Supported browsers: chromium (default), firefox, webkit
- Check browser configuration in `.env`

### Timeout Issues
- Increase EXPLICIT_WAIT in .env
- Check application responsiveness
- Verify network connectivity

### Import Errors
- Ensure virtual environment is activated
- Install all requirements: `pip install -r requirements-dev.txt`
- Add project root to PYTHONPATH if needed

## Contributing

1. Follow PEP 8 code style
2. Use meaningful commit messages
3. Create test cases for new features
4. Ensure all tests pass before submitting PR

## Support

For issues and questions, contact the QA team or check the project documentation.

---

**Last Updated:** 2024
**Framework Version:** 1.0.0
