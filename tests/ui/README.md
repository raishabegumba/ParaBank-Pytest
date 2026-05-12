# UI Test Organization

This directory contains all UI tests for the ParaBank application, organized by functional areas.

## Directory Structure

```
tests/ui/
├── README.md                          # This file
├── conftest.py                        # Main UI test configuration
├── __init__.py                        # UI tests package init
├── login/                             # Login page tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_login.py                  # Main login tests
│   └── test_login_comprehensive.py    # Comprehensive login tests
├── registration/                      # Registration page tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_registration.py           # Main registration tests
│   └── test_registration_comprehensive.py # Comprehensive registration tests
├── accounts/                          # Accounts management tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_accounts_overview.py      # Accounts overview tests
│   ├── test_accounts_overview_comprehensive.py # Comprehensive accounts tests
│   └── test_open_account.py          # Open account tests
├── transfer/                          # Transfer funds tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_transfer_funds.py         # Main transfer tests
│   └── test_transfer_funds_comprehensive.py # Comprehensive transfer tests
├── bill_pay/                          # Bill pay tests
│   ├── __init__.py
│   ├── conftest.py
│   └── test_bill_pay.py              # Bill pay tests
├── loan/                              # Loan request tests
│   ├── __init__.py
│   ├── conftest.py
│   └── test_loan_request.py          # Loan request tests
├── transactions/                      # Find transactions tests
│   ├── __init__.py
│   ├── conftest.py
│   └── test_find_transactions.py     # Find transactions tests
└── workflows/                         # End-to-end workflow tests
    ├── __init__.py
    ├── conftest.py
    ├── test_end_to_end_workflows.py  # End-to-end workflow tests
    └── test_security_comprehensive.py # Security tests
```

## Test Categories

### Smoke Tests
Basic functionality tests that verify core features work:
- Page loading
- Element visibility
- Basic interactions

### Regression Tests
Comprehensive tests that cover:
- Error handling
- Validation
- Edge cases
- Business rules

### Accessibility Tests
Tests that verify:
- WCAG compliance
- Screen reader compatibility
- Keyboard navigation
- Form labeling

### Performance Tests
Tests that measure:
- Page load times
- Response times
- Data retrieval speed

### Security Tests
Tests that verify:
- Data privacy
- Password masking
- Secure form handling

### Integration Tests
End-to-end workflow tests that verify:
- Complete user journeys
- Cross-page functionality
- Data flow between pages

## Running Tests

### Run All UI Tests
```bash
pytest tests/ui/ -v
```

### Run Tests by Category
```bash
# Smoke tests only
pytest tests/ui/ -m smoke -v

# Regression tests only
pytest tests/ui/ -m regression -v

# Accessibility tests only
pytest tests/ui/ -m accessibility -v

# Performance tests only
pytest tests/ui/ -m performance -v

# Security tests only
pytest tests/ui/ -m security -v

# Integration tests only
pytest tests/ui/ -m integration -v
```

### Run Tests by Functional Area
```bash
# Login tests
pytest tests/ui/login/ -v

# Registration tests
pytest tests/ui/registration/ -v

# Account management tests
pytest tests/ui/accounts/ -v

# Transfer funds tests
pytest tests/ui/transfer/ -v

# Bill pay tests
pytest tests/ui/bill_pay/ -v

# Loan request tests
pytest tests/ui/loan/ -v

# Transaction search tests
pytest tests/ui/transactions/ -v

# Workflow tests
pytest tests/ui/workflows/ -v
```

### Run Tests with Reports
```bash
# HTML report
pytest tests/ui/ -v --html=reports/ui_test_report.html

# Coverage report
pytest tests/ui/ -v --cov=src --cov-report=html

# JUnit XML report
pytest tests/ui/ -v --junitxml=reports/ui_test_results.xml
```

## Test Markers

The following pytest markers are used to categorize tests:

- `@pytest.mark.smoke` - Basic functionality tests
- `@pytest.mark.regression` - Comprehensive regression tests
- `@pytest.mark.ui` - UI tests (automatically applied)
- `@pytest.mark.accessibility` - Accessibility compliance tests
- `@pytest.mark.performance` - Performance measurement tests
- `@pytest.mark.security` - Security validation tests
- `@pytest.mark.usability` - Usability tests
- `@pytest.mark.navigation` - Navigation tests
- `@pytest.mark.error_handling` - Error handling tests
- `@pytest.mark.browser_compatibility` - Browser compatibility tests
- `@pytest.mark.localization` - Localization tests
- `@pytest.mark.responsive` - Responsive design tests
- `@pytest.mark.edge_case` - Edge case tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.conditional` - Conditional tests
- `@pytest.mark.business_rules` - Business rules tests
- `@pytest.mark.data_validation` - Data validation tests
- `@pytest.mark.data_filtering` - Data filtering tests
- `@pytest.mark.advanced_search` - Advanced search tests
- `@pytest.mark.data_export` - Data export tests
- `@pytest.mark.data_analysis` - Data analysis tests

## Configuration

### Environment Variables
- `PARABANK_BASE_URL` - Base URL for the application (default: https://parabank.parasoft.com)
- `TEST_TIMEOUT` - Default timeout for page elements (default: 30000ms)
- `HEADLESS` - Run browser in headless mode (default: true)
- `SLOW_MO` - Slow down browser operations (default: 0ms)
- `SCREENSHOT_ON_FAILURE` - Take screenshots on test failure (default: true)
- `VIDEO_ON_FAILURE` - Record video on test failure (default: false)
- `TRACE_ON_FAILURE` - Enable trace on test failure (default: false)

### Browser Configuration
Tests are configured to run with:
- Chrome/Chromium browser
- 1920x1080 viewport
- Ignore HTTPS errors
- JavaScript enabled
- Accept downloads

## Test Data

Test data is managed through:
- `src/utils/test_data_utils.py` - Test data utilities
- `test_data/test_data.json` - Static test data
- Dynamic data generation in fixtures

## Best Practices

1. **Page Object Model**: All tests use page objects for maintainability
2. **Proper Assertions**: Clear, meaningful assertions with descriptive messages
3. **Error Handling**: Robust error handling and validation
4. **Test Isolation**: Each test is independent and can run alone
5. **Cleanup**: Proper cleanup after each test
6. **Logging**: Comprehensive logging for debugging
7. **Screenshots**: Automatic screenshots on failure
8. **Markers**: Proper use of pytest markers for test categorization

## Adding New Tests

1. Determine the appropriate functional area
2. Create test file in the corresponding subdirectory
3. Follow the naming convention: `test_<feature>.py`
4. Use appropriate pytest markers
5. Include comprehensive test coverage
6. Add documentation for complex test scenarios
7. Update this README if adding new functional areas

## Troubleshooting

### Common Issues
- **Element not found**: Check locators and wait strategies
- **Timeout errors**: Increase timeout or check element visibility
- **Test flakiness**: Add proper waits and assertions
- **Browser issues**: Check browser configuration and versions

### Debug Mode
Run tests with additional logging:
```bash
pytest tests/ui/ -v -s --tb=long
```

### Headful Mode
Run tests with visible browser:
```bash
HEADLESS=false pytest tests/ui/ -v
```
