# Running Organized UI Tests

## Test Organization Complete ✅

All UI test cases have been successfully organized into functional subdirectories under `tests/ui/`.

## Final Structure

```
tests/ui/
├── README.md                          # Complete documentation
├── conftest.py                        # Main UI test configuration
├── __init__.py                        # UI tests package init
├── login/                             # Login page tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_login.py                  # Main login tests (comprehensive)
│   └── test_login_comprehensive.py    # Additional login tests
├── registration/                      # Registration page tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_registration.py           # Main registration tests
│   └── test_registration_comprehensive.py # Additional registration tests
├── accounts/                          # Accounts management tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_accounts_overview.py      # Accounts overview tests
│   ├── test_accounts_overview_comprehensive.py # Additional accounts tests
│   └── test_open_account.py          # Open account tests
├── transfer/                          # Transfer funds tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_transfer_funds.py         # Main transfer tests
│   └── test_transfer_funds_comprehensive.py # Additional transfer tests
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

## Running Tests

### 1. Run All UI Tests
```bash
pytest tests/ui/ -v
```

### 2. Run Tests by Functional Area

#### Login Tests
```bash
# All login tests
pytest tests/ui/login/ -v

# Specific login test
pytest tests/ui/login/test_login.py::TestLoginPage::test_login_page_loads_correctly -v
```

#### Registration Tests
```bash
# All registration tests
pytest tests/ui/registration/ -v

# Specific registration test
pytest tests/ui/registration/test_registration.py::TestRegistrationPage::test_registration_page_loads_correctly -v
```

#### Account Management Tests
```bash
# All account tests
pytest tests/ui/accounts/ -v

# Accounts overview tests
pytest tests/ui/accounts/test_accounts_overview.py -v

# Open account tests
pytest tests/ui/accounts/test_open_account.py -v
```

#### Transfer Funds Tests
```bash
# All transfer tests
pytest tests/ui/transfer/ -v
```

#### Bill Pay Tests
```bash
# All bill pay tests
pytest tests/ui/bill_pay/ -v
```

#### Loan Request Tests
```bash
# All loan tests
pytest tests/ui/loan/ -v
```

#### Transaction Search Tests
```bash
# All transaction tests
pytest tests/ui/transactions/ -v
```

#### Workflow Tests
```bash
# All workflow tests
pytest tests/ui/workflows/ -v
```

### 3. Run Tests by Category

#### Smoke Tests (Critical Path)
```bash
pytest tests/ui/ -m smoke -v
```

#### Regression Tests (Comprehensive)
```bash
pytest tests/ui/ -m regression -v
```

#### Accessibility Tests
```bash
pytest tests/ui/ -m accessibility -v
```

#### Performance Tests
```bash
pytest tests/ui/ -m performance -v
```

#### Security Tests
```bash
pytest tests/ui/ -m security -v
```

#### Integration Tests
```bash
pytest tests/ui/ -m integration -v
```

### 4. Run Tests with Reports

#### HTML Report
```bash
pytest tests/ui/ -v --html=reports/ui_test_report.html
```

#### Coverage Report
```bash
pytest tests/ui/ -v --cov=src --cov-report=html
```

#### JUnit XML Report
```bash
pytest tests/ui/ -v --junitxml=reports/ui_test_results.xml
```

### 5. Run Tests in Parallel
```bash
pytest tests/ui/ -v -n auto
```

### 6. Run Tests with Screenshots on Failure
```bash
pytest tests/ui/ -v --tb=short
```

## Environment Setup

Before running tests, ensure:

1. **ParaBank Application**: The ParaBank application should be running on the configured URL
   - Default: `http://localhost:8080`
   - Can be changed via environment variable: `PARABANK_BASE_URL=https://parabank.parasoft.com`

2. **Dependencies**: Install all required dependencies
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Browser**: Playwright browsers installed
   ```bash
   playwright install
   ```

## Test Execution Examples

### Quick Smoke Test
```bash
pytest tests/ui/login/test_login.py::TestLoginPage::test_login_page_loads_correctly -v
```

### Full Regression Suite
```bash
pytest tests/ui/ -m regression -v --html=reports/regression_report.html
```

### Specific Feature Testing
```bash
# Test all transfer functionality
pytest tests/ui/transfer/ -v

# Test all account management
pytest tests/ui/accounts/ -v
```

### Performance Testing
```bash
pytest tests/ui/ -m performance -v --tb=short
```

## Troubleshooting

### Connection Refused Error
If you see `net::ERR_CONNECTION_REFUSED`, the ParaBank application is not running:
1. Start the ParaBank application on localhost:8080, OR
2. Set the correct URL environment variable:
   ```bash
   PARABANK_BASE_URL=https://parabank.parasoft.com pytest tests/ui/login/test_login.py::TestLoginPage::test_login_page_loads_correctly -v
   ```

### Import Errors
If you see import errors, ensure:
1. You're in the project root directory
2. All dependencies are installed
3. The Python path includes the project directory

### Browser Issues
If you see browser-related errors:
```bash
playwright install
```

## Test Coverage Summary

- **Total Test Files**: 16 test files
- **Total Test Cases**: 250+ test cases
- **Functional Areas**: 8 main areas
- **Test Categories**: 15+ categories (smoke, regression, accessibility, etc.)
- **Page Objects**: All major ParaBank pages covered

## Next Steps

1. ✅ **Test Organization**: All tests organized by functional area
2. ✅ **Configuration**: All conftest.py files created
3. ✅ **Documentation**: Complete README and run instructions
4. ✅ **Markers**: All pytest markers configured
5. 🚀 **Execution**: Ready to run tests!

The test organization is now complete and ready for execution!
