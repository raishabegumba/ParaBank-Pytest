"""Root pytest configuration — plugin registration and session-level fixtures."""
import pytest
import requests
from src.config.settings import settings

# ---------------------------------------------------------------------------
# Plugin registration
# ---------------------------------------------------------------------------

pytest_plugins = [
    "src.fixtures.browser_fixtures",
    "src.fixtures.reporting_fixtures",
    "src.fixtures.test_data_fixtures",
]


# ---------------------------------------------------------------------------
# Session helpers
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def test_env():
    """Return test environment from settings."""
    return settings.test_env


@pytest.fixture(scope="session", autouse=True)
def initialize_parabank_db():
    """Reset ParaBank database once before the entire test session."""
    try:
        response = requests.post(
            f"{settings.base_url}/services/bank/initializeDB",
            timeout=10,
        )
        if response.status_code == 200:
            print("\nParaBank DB initialized successfully")
        else:
            print(f"\nDB init returned status: {response.status_code}")
    except Exception as e:
        print(f"\nDB init failed (continuing anyway): {e}")
    yield


@pytest.fixture(scope="session", autouse=True)
def cleanup():
    """Session-level cleanup hook (extend as needed)."""
    yield
    # Add any post-session cleanup here


# ---------------------------------------------------------------------------
# Reporting hook
# ---------------------------------------------------------------------------

def pytest_runtest_makereport(item, call):
    """Attach call report to the item so fixtures can inspect pass/fail."""
    if call.excinfo is not None:
        item.rep_call = call   # fixed: was incorrectly storing `item` instead of `call`