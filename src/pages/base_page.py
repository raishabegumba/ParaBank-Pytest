"""Base classes for Playwright-based testing."""
from playwright.sync_api import Page, expect
from src.config.logger import log


class BasePage:
    """Base page class with common functionality for all page objects."""

    def __init__(self, page: Page):
        """Initialize the page object."""
        self.page = page
        self.log = log

    def goto(self, url: str):
        """Navigate to URL.

        ParaBank pages can be slow/flaky; avoid waiting for full `load` by
        defaulting to `domcontentloaded`.
        """
        try:
            self.page.goto(url, wait_until="domcontentloaded")
            self.log.info(f"Navigated to {url}")
        except Exception as e:
            self.log.error(f"Failed to navigate to {url}. Error: {e}")
            raise


    def find_element(self, selector: str, timeout: int = 10000):
        """Find element."""
        try:
            locator = self.page.locator(selector)
            locator.wait_for(timeout=timeout)
            self.log.info(f"Found element: {selector}")
            return locator
        except Exception as e:
            self.log.error(f"Failed to find element: {selector}. Error: {e}")
            raise

    def find_elements(self, selector: str):
        """Find multiple elements."""
        try:
            locator = self.page.locator(selector)
            elements = locator.all()
            self.log.info(f"Found {len(elements)} elements: {selector}")
            return elements
        except Exception as e:
            self.log.error(f"Failed to find elements: {selector}. Error: {e}")
            raise

    def click(self, selector: str):
        """Click element."""
        try:
            locator = self.page.locator(selector)
            locator.click()
            self.log.info(f"Clicked element: {selector}")
        except Exception as e:
            self.log.error(f"Failed to click element: {selector}. Error: {e}")
            raise

    def fill(self, selector: str, text: str):
        """Fill text in input field."""
        try:
            locator = self.page.locator(selector)
            locator.fill(text)
            self.log.info(f"Filled text '{text}' in element: {selector}")
        except Exception as e:
            self.log.error(f"Failed to fill text in element: {selector}. Error: {e}")
            raise

    def get_text(self, selector: str) -> str:
        """Get text from element."""
        try:
            locator = self.page.locator(selector)
            text = locator.text_content()
            self.log.info(f"Retrieved text '{text}' from element: {selector}")
            return text
        except Exception as e:
            self.log.error(f"Failed to get text from element: {selector}. Error: {e}")
            raise

    def is_visible(self, selector: str, timeout: int = 10000) -> bool:
        """Check if element is visible."""
        try:
            locator = self.page.locator(selector)
            locator.is_visible(timeout=timeout)
            self.log.info(f"Element is visible: {selector}")
            return True
        except Exception:
            self.log.warning(f"Element is not visible: {selector}")
            return False

    def is_enabled(self, selector: str) -> bool:
        """Check if element is enabled."""
        try:
            locator = self.page.locator(selector)
            is_enabled = locator.is_enabled()
            self.log.info(f"Element is enabled: {selector}")
            return is_enabled
        except Exception as e:
            self.log.error(f"Failed to check if element is enabled: {selector}. Error: {e}")
            raise

    def scroll_to_element(self, selector: str):
        """Scroll to element."""
        try:
            locator = self.page.locator(selector)
            locator.scroll_into_view_if_needed()
            self.log.info(f"Scrolled to element: {selector}")
        except Exception as e:
            self.log.error(f"Failed to scroll to element: {selector}. Error: {e}")
            raise

    def wait_for_element(self, selector: str, timeout: int = 10000):
        """Wait for element to be present."""
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            self.log.info(f"Element is present: {selector}")
        except Exception as e:
            self.log.error(f"Failed waiting for element: {selector}. Error: {e}")
            raise

    def take_screenshot(self, filename: str):
        """Take screenshot of current page."""
        try:
            self.page.screenshot(path=f"reports/screenshots/{filename}.png")
            self.log.info(f"Screenshot saved: {filename}")
        except Exception as e:
            self.log.error(f"Failed to take screenshot. Error: {e}")
            raise

    def get_url(self) -> str:
        """Get current URL."""
        return self.page.url

    def get_title(self) -> str:
        """Get current page title."""
        return self.page.title

    def refresh_page(self):
        """Refresh the page."""
        self.page.reload()
        self.log.info("Page refreshed")

    def go_back(self):
        """Navigate back."""
        self.page.go_back()
        self.log.info("Navigated back")

    def go_forward(self):
        """Navigate forward."""
        self.page.go_forward()
        self.log.info("Navigated forward")

    def press_key(self, selector: str, key: str):
        """Press key on element."""
        try:
            locator = self.page.locator(selector)
            locator.press(key)
            self.log.info(f"Pressed key '{key}' on element: {selector}")
        except Exception as e:
            self.log.error(f"Failed to press key on element: {selector}. Error: {e}")
            raise

    def get_attribute(self, selector: str, attribute: str) -> str:
        """Get attribute value from element."""
        try:
            locator = self.page.locator(selector)
            value = locator.get_attribute(attribute)
            self.log.info(f"Retrieved attribute '{attribute}' value: {value}")
            return value
        except Exception as e:
            self.log.error(f"Failed to get attribute from element: {selector}. Error: {e}")
            raise

    def check(self, selector: str):
        """Check checkbox or radio button."""
        try:
            locator = self.page.locator(selector)
            locator.check()
            self.log.info(f"Checked element: {selector}")
        except Exception as e:
            self.log.error(f"Failed to check element: {selector}. Error: {e}")
            raise

    def uncheck(self, selector: str):
        """Uncheck checkbox."""
        try:
            locator = self.page.locator(selector)
            locator.uncheck()
            self.log.info(f"Unchecked element: {selector}")
        except Exception as e:
            self.log.error(f"Failed to uncheck element: {selector}. Error: {e}")
            raise
