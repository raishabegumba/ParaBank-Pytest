"""Advanced wait strategies and synchronization utilities."""
import time
from typing import Callable, Any, Optional, Union
from playwright.sync_api import Page, Locator, expect
from src.config.settings import get_settings
from src.config.logger import log


class WaitStrategy:
    """Enumeration of different wait strategies."""
    
    ELEMENT_VISIBLE = "visible"
    ELEMENT_HIDDEN = "hidden"
    ELEMENT_CLICKABLE = "clickable"
    ELEMENT_ENABLED = "enabled"
    ELEMENT_DISABLED = "disabled"
    ELEMENT_ATTACHED = "attached"
    ELEMENT_DETACHED = "detached"


class WaitHelper:
    """Advanced wait helper with multiple strategies and retry logic."""
    
    def __init__(self, page: Page):
        """Initialize wait helper with page instance."""
        self.page = page
        self.settings = get_settings()
        self.default_timeout = self.settings.explicit_wait
        
    def wait_for_element(
        self,
        selector: str,
        strategy: str = WaitStrategy.ELEMENT_VISIBLE,
        timeout: Optional[int] = None,
        message: Optional[str] = None
    ) -> Locator:
        """
        Wait for element with specified strategy.
        
        Args:
            selector: CSS selector or XPath
            strategy: Wait strategy from WaitStrategy enum
            timeout: Custom timeout in milliseconds
            message: Custom error message
            
        Returns:
            Locator object for the element
        """
        timeout = timeout or self.default_timeout
        locator = self.page.locator(selector)
        
        try:
            if strategy == WaitStrategy.ELEMENT_VISIBLE:
                locator.wait_for(state="visible", timeout=timeout)
            elif strategy == WaitStrategy.ELEMENT_HIDDEN:
                locator.wait_for(state="hidden", timeout=timeout)
            elif strategy == WaitStrategy.ELEMENT_CLICKABLE:
                locator.wait_for(state="visible", timeout=timeout)
                expect(locator).to_be_enabled(timeout=timeout)
            elif strategy == WaitStrategy.ELEMENT_ENABLED:
                expect(locator).to_be_enabled(timeout=timeout)
            elif strategy == WaitStrategy.ELEMENT_DISABLED:
                expect(locator).to_be_disabled(timeout=timeout)
            elif strategy == WaitStrategy.ELEMENT_ATTACHED:
                locator.wait_for(state="attached", timeout=timeout)
            elif strategy == WaitStrategy.ELEMENT_DETACHED:
                locator.wait_for(state="detached", timeout=timeout)
            else:
                raise ValueError(f"Unknown wait strategy: {strategy}")
                
            log.info(f"Element {selector} found with strategy {strategy}")
            return locator
            
        except Exception as e:
            error_msg = message or f"Failed to wait for element {selector} with strategy {strategy}"
            log.error(f"{error_msg}: {e}")
            raise TimeoutError(error_msg) from e
    
    def wait_for_text(
        self,
        selector: str,
        expected_text: str,
        timeout: Optional[int] = None,
        exact_match: bool = False
    ) -> bool:
        """
        Wait for element to contain specific text.
        
        Args:
            selector: Element selector
            expected_text: Text to wait for
            timeout: Custom timeout
            exact_match: Whether to match exact text
            
        Returns:
            True if text found, False otherwise
        """
        timeout = timeout or self.default_timeout
        locator = self.page.locator(selector)
        
        try:
            if exact_match:
                expect(locator).to_have_text(expected_text, timeout=timeout)
            else:
                expect(locator).to_contain_text(expected_text, timeout=timeout)
            
            log.info(f"Text '{expected_text}' found in element {selector}")
            return True
            
        except Exception as e:
            log.error(f"Failed to wait for text '{expected_text}' in element {selector}: {e}")
            return False
    
    def wait_for_url_change(
        self,
        expected_url: Optional[str] = None,
        timeout: Optional[int] = None,
        wait_until: str = "load"
    ) -> bool:
        """
        Wait for URL to change to expected value.
        
        Args:
            expected_url: Expected URL (None for any change)
            timeout: Custom timeout
            wait_until: Navigation wait condition
            
        Returns:
            True if URL changed as expected
        """
        timeout = timeout or self.default_timeout
        initial_url = self.page.url
        
        try:
            if expected_url:
                self.page.wait_for_url(expected_url, timeout=timeout, wait_until=wait_until)
                log.info(f"URL changed to: {expected_url}")
            else:
                # Wait for any URL change
                self.page.wait_for_function(
                    f"() => window.location.href !== '{initial_url}'",
                    timeout=timeout
                )
                log.info(f"URL changed from {initial_url} to {self.page.url}")
            
            return True
            
        except Exception as e:
            log.error(f"Failed to wait for URL change: {e}")
            return False
    
    def wait_for_page_load(
        self,
        timeout: Optional[int] = None,
        wait_until: str = "load"
    ) -> bool:
        """
        Wait for page to fully load.
        
        Args:
            timeout: Custom timeout
            wait_until: Load state ('load', 'domcontentloaded', 'networkidle')
            
        Returns:
            True if page loaded successfully
        """
        timeout = timeout or self.default_timeout
        
        try:
            self.page.wait_for_load_state(wait_until, timeout=timeout)
            log.info(f"Page loaded successfully with state: {wait_until}")
            return True
            
        except Exception as e:
            log.error(f"Failed to wait for page load: {e}")
            return False
    
    def wait_for_network_idle(self, timeout: Optional[int] = None) -> bool:
        """
        Wait for network to be idle.
        
        Args:
            timeout: Custom timeout
            
        Returns:
            True if network is idle
        """
        return self.wait_for_page_load(timeout=timeout, wait_until="networkidle")
    
    def wait_for_element_count(
        self,
        selector: str,
        expected_count: int,
        timeout: Optional[int] = None
    ) -> bool:
        """
        Wait for specific number of elements to be present.
        
        Args:
            selector: Element selector
            expected_count: Expected number of elements
            timeout: Custom timeout
            
        Returns:
            True if count matches expected
        """
        timeout = timeout or self.default_timeout
        locator = self.page.locator(selector)
        
        try:
            expect(locator).to_have_count(expected_count, timeout=timeout)
            log.info(f"Element count {expected_count} found for selector {selector}")
            return True
            
        except Exception as e:
            log.error(f"Failed to wait for element count {expected_count}: {e}")
            return False
    
    def wait_for_attribute_value(
        self,
        selector: str,
        attribute: str,
        expected_value: str,
        timeout: Optional[int] = None
    ) -> bool:
        """
        Wait for element to have specific attribute value.
        
        Args:
            selector: Element selector
            attribute: Attribute name
            expected_value: Expected attribute value
            timeout: Custom timeout
            
        Returns:
            True if attribute value matches
        """
        timeout = timeout or self.default_timeout
        locator = self.page.locator(selector)
        
        try:
            expect(locator).to_have_attribute(attribute, expected_value, timeout=timeout)
            log.info(f"Attribute {attribute}='{expected_value}' found for element {selector}")
            return True
            
        except Exception as e:
            log.error(f"Failed to wait for attribute {attribute}='{expected_value}': {e}")
            return False
    
    def wait_for_custom_condition(
        self,
        condition: Callable[[], bool],
        timeout: Optional[int] = None,
        poll_interval: float = 0.5,
        message: Optional[str] = None
    ) -> bool:
        """
        Wait for custom condition to be true.
        
        Args:
            condition: Function that returns boolean
            timeout: Custom timeout in milliseconds
            poll_interval: Polling interval in seconds
            message: Custom error message
            
        Returns:
            True if condition met, False otherwise
        """
        timeout = timeout or self.default_timeout
        timeout_seconds = timeout / 1000
        start_time = time.time()
        
        try:
            while time.time() - start_time < timeout_seconds:
                if condition():
                    log.info("Custom condition met")
                    return True
                time.sleep(poll_interval)
            
            error_msg = message or "Custom condition not met within timeout"
            log.error(error_msg)
            return False
            
        except Exception as e:
            error_msg = message or f"Error while waiting for custom condition: {e}"
            log.error(error_msg)
            return False
    
    def wait_for_and_click(
        self,
        selector: str,
        timeout: Optional[int] = None,
        wait_strategy: str = WaitStrategy.ELEMENT_CLICKABLE
    ) -> bool:
        """
        Wait for element to be clickable and then click it.
        
        Args:
            selector: Element selector
            timeout: Custom timeout
            wait_strategy: Wait strategy before clicking
            
        Returns:
            True if clicked successfully
        """
        try:
            locator = self.wait_for_element(
                selector=selector,
                strategy=wait_strategy,
                timeout=timeout
            )
            locator.click()
            log.info(f"Successfully clicked element: {selector}")
            return True
            
        except Exception as e:
            log.error(f"Failed to wait for and click element {selector}: {e}")
            return False
    
    def wait_for_and_fill(
        self,
        selector: str,
        text: str,
        timeout: Optional[int] = None,
        clear_first: bool = True
    ) -> bool:
        """
        Wait for element and fill it with text.
        
        Args:
            selector: Element selector
            text: Text to fill
            timeout: Custom timeout
            clear_first: Whether to clear field first
            
        Returns:
            True if filled successfully
        """
        try:
            locator = self.wait_for_element(
                selector=selector,
                strategy=WaitStrategy.ELEMENT_VISIBLE,
                timeout=timeout
            )
            
            if clear_first:
                locator.clear()
            
            locator.fill(text)
            log.info(f"Successfully filled element {selector} with text: {text}")
            return True
            
        except Exception as e:
            log.error(f"Failed to wait for and fill element {selector}: {e}")
            return False


def create_wait_helper(page: Page) -> WaitHelper:
    """
    Factory function to create WaitHelper instance.
    
    Args:
        page: Playwright page instance
        
    Returns:
        WaitHelper instance
    """
    return WaitHelper(page)
