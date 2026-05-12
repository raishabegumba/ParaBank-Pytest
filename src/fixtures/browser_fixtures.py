"""Enterprise-grade browser fixtures for Playwright testing."""
import pytest
import os
from typing import Generator, Optional, Dict, Any
from playwright.sync_api import Browser, BrowserContext, Page
from src.config.settings import get_settings
from src.config.logger import log
from src.utils.screenshot_manager import ScreenshotManager
from src.utils.webdriver_utils import get_browser, get_browser_context, create_screenshots_directory


@pytest.fixture(scope="session")
def browser_instance() -> Generator[Browser, None, None]:
    """
    Session-scoped browser fixture.
    
    Yields:
        Browser instance for the entire test session
    """
    try:
        settings = get_settings()
        create_screenshots_directory()
        
        # Initialize browser with settings
        browser = get_browser()
        
        log.info(f"Browser session started: {settings.browser.value}")
        yield browser
        
    except Exception as e:
        log.error(f"Failed to initialize browser: {e}")
        raise
    finally:
        try:
            browser.close()
            log.info("Browser session closed")
        except:
            pass


@pytest.fixture(scope="function")
def browser_context(browser_instance: Browser) -> Generator[BrowserContext, None, None]:
    """
    Function-scoped browser context fixture.
    
    Args:
        browser_instance: Session browser instance
        
    Yields:
        Browser context instance
    """
    try:
        settings = get_settings()
        
        # Create context with configured settings
        context = get_browser_context(browser_instance)
        
        # Add extra context settings if needed
        if settings.slow_mo > 0:
            context.set_default_timeout(settings.slow_mo)
        
        log.info("Browser context created")
        yield context
        
    except Exception as e:
        log.error(f"Failed to create browser context: {e}")
        raise
    finally:
        try:
            context.close()
            log.info("Browser context closed")
        except:
            pass


@pytest.fixture(scope="function")
def page(browser_context: BrowserContext) -> Generator[Page, None, None]:
    """
    Function-scoped page fixture.
    
    Args:
        browser_context: Browser context instance
        
    Yields:
        Page instance
    """
    try:
        settings = get_settings()
        
        # Create new page
        page = browser_context.new_page()
        
        # Set default timeouts
        page.set_default_timeout(settings.explicit_wait)
        page.set_default_navigation_timeout(settings.navigation_timeout)
        
        # Navigate to base URL if configured
        if hasattr(settings, 'base_url') and settings.base_url:
            page.goto(settings.base_url)
        
        log.info("Page instance created")
        yield page
        
    except Exception as e:
        log.error(f"Failed to create page: {e}")
        raise
    finally:
        try:
            page.close()
            log.info("Page instance closed")
        except:
            pass


@pytest.fixture(scope="function")
def screenshot_manager(page: Page) -> ScreenshotManager:
    """
    Screenshot manager fixture.
    
    Args:
        page: Page instance
        
    Returns:
        ScreenshotManager instance
    """
    return ScreenshotManager(page)


@pytest.fixture(scope="function")
def mobile_page(browser_context: BrowserContext) -> Generator[Page, None, None]:
    """
    Mobile viewport page fixture.
    
    Args:
        browser_context: Browser context instance
        
    Yields:
        Page instance with mobile viewport
    """
    try:
        settings = get_settings()
        
        # Create mobile context
        mobile_context = browser_context.browser.new_context(
            viewport={'width': 375, 'height': 667},  # iPhone dimensions
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        )
        
        page = mobile_context.new_page()
        page.set_default_timeout(settings.explicit_wait)
        
        log.info("Mobile page instance created")
        yield page
        
    except Exception as e:
        log.error(f"Failed to create mobile page: {e}")
        raise
    finally:
        try:
            page.close()
            mobile_context.close()
            log.info("Mobile page instance closed")
        except:
            pass


@pytest.fixture(scope="function")
def authenticated_page(browser_context: BrowserContext) -> Generator[Page, None, None]:
    """
    Pre-authenticated page fixture.
    
    Args:
        browser_context: Browser context instance
        
    Yields:
        Page instance with authenticated session
    """
    try:
        settings = get_settings()
        
        # Create page and authenticate
        page = browser_context.new_page()
        page.set_default_timeout(settings.explicit_wait)
        
        # Navigate to login page
        page.goto(f"{settings.base_url}/index.htm")
        
        # Perform login
        page.fill("#username", settings.test_username)
        page.fill("#password", settings.test_password)
        page.click("input[type='submit'][value='Log In']")
        
        # Wait for login completion
        page.wait_for_selector("#rightPanel h1", timeout=10000)
        
        log.info("Authenticated page instance created")
        yield page
        
    except Exception as e:
        log.error(f"Failed to create authenticated page: {e}")
        raise
    finally:
        try:
            page.close()
            log.info("Authenticated page instance closed")
        except:
            pass


@pytest.fixture(scope="session")
def browser_options() -> Dict[str, Any]:
    """
    Browser options fixture for configuration.
    
    Returns:
        Dictionary of browser options
    """
    settings = get_settings()
    
    return {
        'headless': settings.headless,
        'slow_mo': settings.slow_mo,
        'ignore_https_errors': settings.ignore_https_errors,
        'viewport': {
            'width': settings.window_width,
            'height': settings.window_height
        }
    }


@pytest.fixture(scope="function", autouse=True)
def page_cleanup(page: Page):
    """
    Automatic page cleanup fixture.
    
    Args:
        page: Page instance to cleanup
    """
    yield
    
    try:
        # Clear any open dialogs/modals
        page.evaluate("""
            // Close any open modals or dialogs
            const modals = document.querySelectorAll('.modal, .dialog, [role="dialog"]');
            modals.forEach(modal => modal.style.display = 'none');
            
            // Clear any alerts
            if (window.alert) {
                window.alert = function() {};
            }
        """)
        
        # Clear local storage and session storage
        page.evaluate("""
            localStorage.clear();
            sessionStorage.clear();
        """)
        
        log.debug("Page cleanup completed")
        
    except Exception as e:
        log.warning(f"Page cleanup failed: {e}")


@pytest.fixture(scope="function")
def network_conditions():
    """
    Network conditions fixture for testing different network scenarios.
    
    Returns:
        Dictionary with network condition presets
    """
    return {
        'slow_3g': {
            'download': 500 * 1024,  # 500 Kbps
            'upload': 500 * 1024,    # 500 Kbps
            'latency': 400            # 400ms
        },
        'fast_3g': {
            'download': 1.6 * 1024 * 1024,  # 1.6 Mbps
            'upload': 750 * 1024,           # 750 Kbps
            'latency': 150                   # 150ms
        },
        'offline': {
            'offline': True
        }
    }


@pytest.fixture(scope="function")
def browser_with_network_conditions(
    browser_context: BrowserContext,
    network_conditions: Dict[str, Any]
) -> callable:
    """
    Fixture to apply network conditions to browser context.
    
    Args:
        browser_context: Browser context instance
        network_conditions: Network condition presets
        
    Returns:
        Function to apply network conditions
    """
    def apply_conditions(condition_name: str):
        """Apply specific network condition."""
        if condition_name in network_conditions:
            conditions = network_conditions[condition_name]
            
            if 'offline' in conditions and conditions['offline']:
                browser_context.set_offline(True)
                log.info(f"Applied offline network condition")
            else:
                browser_context.route('**/*', lambda route: route.fulfill())
                # Note: Full network throttling requires additional setup
                log.info(f"Applied network condition: {condition_name}")
        else:
            log.warning(f"Unknown network condition: {condition_name}")
    
    return apply_conditions


@pytest.fixture(scope="session")
def browser_capabilities():
    """
    Browser capabilities fixture for reporting.
    
    Returns:
        Dictionary of browser capabilities
    """
    settings = get_settings()
    
    return {
        'browser_name': settings.browser.value,
        'browser_version': 'unknown',  # Could be detected
        'platform': os.name,
        'headless': settings.headless,
        'viewport': f"{settings.window_width}x{settings.window_height}",
        'user_agent': 'Playwright'
    }
