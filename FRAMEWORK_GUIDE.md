"""Framework documentation and best practices."""

# PyTest Framework Best Practices

## 1. Test Organization

### Directory Structure
- Keep tests organized by feature/module
- Separate UI and API tests
- Use consistent naming conventions

### Test Naming
- Use descriptive names: `test_login_with_valid_credentials()`
- Not: `test_login()` or `test_1()`
- Clearly state what is being tested

## 2. Fixtures and Setup

### Fixture Scope
- Use `function` scope for tests that need fresh state
- Use `session` scope for expensive resources (DB connections)
- Use `module` scope for test data that can be reused

### Fixture Management
- Keep fixtures in conftest.py
- Use `autouse=True` for automatic fixtures
- Implement proper cleanup in fixtures

## 3. Page Object Model

### POM Principles
- One page object per page/component
- Store selectors as class variables (CSS selectors or Playwright locators)
- Create methods for user actions
- Use base page for common operations

### Example
```python
class LoginPage(BasePage):
    USERNAME = "#username"
    LOGIN_BTN = "#login"
    
    def login(self, username, password):
        self.fill(self.USERNAME, username)
        self.click(self.LOGIN_BTN)
```

## 4. Assertions

### Best Practices
- One logical assertion per test (or related assertions)
- Use clear assertion messages
- Test behavior, not implementation
- Avoid assertions on UI elements position

### Example
```python
def test_login_success(self):
    self.page.login("user", "pass")
    assert "dashboard" in self.page.get_url()  # Behavior
    # Not: assert self.page.logo.is_displayed()  # Implementation detail
```

## 5. Test Data

### Data Management
- Use Faker for random data
- Keep test data in JSON files for static data
- Avoid hardcoding data
- Clean up created data after tests

### Example
```python
from src.utils.test_data_utils import load_test_data, generate_random_user

users = load_test_data("test_users")
new_user = generate_random_user()
```

## 6. Error Handling

### Logging
- Log important steps
- Use appropriate log levels
- Include context in logs

### Example
```python
self.log.info("Starting login process")
self.page.fill(self.USERNAME, username)
self.log.debug(f"Entered username: {username}")
```

## 7. Parametrization

### Multiple Test Cases
- Use `@pytest.mark.parametrize` for data-driven tests
- Test multiple scenarios without duplication

### Example
```python
@pytest.mark.parametrize("username,password,expected", [
    ("user1", "pass1", True),
    ("user2", "pass2", True),
    ("invalid", "wrong", False),
])
def test_login(self, username, password, expected):
    result = self.page.login(username, password)
    assert result == expected
```

## 8. Markers

### Test Classification
- `@pytest.mark.smoke` - Critical path tests
- `@pytest.mark.regression` - Comprehensive tests
- `@pytest.mark.ui` - UI tests
- `@pytest.mark.api` - API tests
- `@pytest.mark.slow` - Long running tests

## 9. Configuration

### Environment Management
- Use .env files for configuration
- Never commit sensitive data
- Use environment-specific settings

### Example
```python
from src.config.settings import settings
BASE_URL = settings.base_url
```

## 10. CI/CD Integration

### Pipeline Configuration
- Run tests on every commit
- Run smoke tests for quick feedback
- Generate reports and coverage
- Archive artifacts

### Parallel Execution
```bash
pytest -n auto  # Run tests in parallel
```

## Common Pitfalls to Avoid

1. ❌ Using sleep instead of waits
2. ❌ Hardcoding test data
3. ❌ Complex test methods
4. ❌ Ignoring test failures
5. ❌ Not cleaning up test data
6. ❌ Fragile locators
7. ❌ No logging
8. ❌ Single assertion per file
9. ❌ Shared state between tests
10. ❌ No error handling
