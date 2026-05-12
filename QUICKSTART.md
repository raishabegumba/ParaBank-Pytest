"""Quick Start Guide for ParaBank PyTest Framework"""

# Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
# Activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### Step 2: Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings (optional)
# Most defaults are pre-configured
```

### Step 3: Run Your First Test
```bash
# Run all tests
pytest

# Run only smoke tests
pytest -m smoke

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/ui/test_login.py
```

## Project Layout at a Glance

```
ParaBank-Pytest/
├── src/               ← Application code (pages, API, utilities)
├── tests/             ← Test code (UI, API, performance)
├── test_data/         ← Test data files
├── reports/           ← Generated reports
├── logs/              ← Test logs
├── pytest.ini         ← Pytest configuration
└── README.md          ← Full documentation
```

## Common Commands

### Running Tests
```bash
pytest                          # All tests
pytest -v                       # Verbose
pytest -s                       # Show prints
pytest -x                       # Stop on first failure
pytest --maxfail=3              # Stop after 3 failures
pytest -k "login"               # Run tests matching name
pytest -m smoke                 # Run tests with marker
```

### Generating Reports
```bash
pytest --html=reports/report.html --self-contained-html
pytest --cov=src --cov-report=html
```

### Running in Parallel
```bash
pytest -n auto                  # Auto-detect CPU count
pytest -n 4                     # Use 4 processes
```

## Key Files to Know

| File | Purpose |
|------|---------|
| `src/config/settings.py` | Configuration management |
| `src/pages/base_page.py` | Base class for UI tests |
| `src/api/base_api.py` | Base class for API tests |
| `tests/conftest.py` | Pytest fixtures and setup |
| `pytest.ini` | Pytest configuration |
| `test_data/test_data.json` | Test data |

## Creating Your First Test

### UI Test
```python
# tests/ui/test_sample.py
import pytest
from src.pages.base_page import BasePage

@pytest.mark.smoke
@pytest.mark.ui
def test_page_title(page):
    base_page = BasePage(page)
    assert "ParaBank" in base_page.get_title()
```

### API Test
```python
# tests/api/test_sample.py
import pytest

@pytest.mark.smoke
@pytest.mark.api
def test_api_endpoint(api_client):
    response = api_client.get("/customers")
    assert response.status_code == 200
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Playwright browsers not installed | Run: `playwright install` |
| Import errors | Activate virtual environment: `source venv/bin/activate` |
| Tests timeout | Increase `EXPLICIT_WAIT` in `.env` file |
| Port already in use | Check if application is running on configured port |

## Next Steps

1. Read [README.md](README.md) for detailed documentation
2. Check [FRAMEWORK_GUIDE.md](FRAMEWORK_GUIDE.md) for best practices
3. Review sample tests in `tests/ui/test_login.py` and `tests/api/test_api.py`
4. Create your first test following the patterns

## Resources

- [PyTest Documentation](https://docs.pytest.org/)
- [Selenium Documentation](https://selenium.dev/documentation/)
- [Requests Library](https://requests.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

Happy Testing! 🚀
