"""Advanced assertion helpers for enterprise testing."""
import re
import json
from typing import Any, Optional, Dict, List, Union
from playwright.sync_api import Page, Locator, expect
from src.config.logger import log


class AssertionHelper:
    """Advanced assertion helper with enhanced error messages and validations."""
    
    def __init__(self, page: Page):
        """Initialize assertion helper."""
        self.page = page
    
    
    def assert_element_visible(
        self,
        selector: str,
        timeout: int = 10000,
        message: Optional[str] = None
    ):
        """Assert element is visible."""
        try:
            locator = self.page.locator(selector)
            expect(locator).to_be_visible(timeout=timeout)
            log.info(f"Element {selector} is visible as expected")
        except AssertionError as e:
            error_msg = message or f"Element {selector} should be visible but is not"
            log.error(error_msg)
            raise AssertionError(error_msg) from e
    
    def assert_element_hidden(
        self,
        selector: str,
        timeout: int = 10000,
        message: Optional[str] = None
    ):
        """Assert element is hidden."""
        try:
            locator = self.page.locator(selector)
            expect(locator).to_be_hidden(timeout=timeout)
            log.info(f"Element {selector} is hidden as expected")
        except AssertionError as e:
            error_msg = message or f"Element {selector} should be hidden but is visible"
            log.error(error_msg)
            raise AssertionError(error_msg) from e
    
    def assert_element_enabled(
        self,
        selector: str,
        timeout: int = 10000,
        message: Optional[str] = None
    ):
        """Assert element is enabled."""
        try:
            locator = self.page.locator(selector)
            expect(locator).to_be_enabled(timeout=timeout)
            log.info(f"Element {selector} is enabled as expected")
        except AssertionError as e:
            error_msg = message or f"Element {selector} should be enabled but is disabled"
            log.error(error_msg)
            raise AssertionError(error_msg) from e
    
    def assert_element_disabled(
        self,
        selector: str,
        timeout: int = 10000,
        message: Optional[str] = None
    ):
        """Assert element is disabled."""
        try:
            locator = self.page.locator(selector)
            expect(locator).to_be_disabled(timeout=timeout)
            log.info(f"Element {selector} is disabled as expected")
        except AssertionError as e:
            error_msg = message or f"Element {selector} should be disabled but is enabled"
            log.error(error_msg)
            raise AssertionError(error_msg) from e
    
    def assert_element_contains_text(
        self,
        selector: str,
        expected_text: str,
        timeout: int = 10000,
        case_sensitive: bool = True,
        message: Optional[str] = None
    ):
        """Assert element contains specific text."""
        try:
            locator = self.page.locator(selector)
            if case_sensitive:
                expect(locator).to_contain_text(expected_text, timeout=timeout)
            else:
                actual_text = locator.text_content(timeout=timeout)
                if expected_text.lower() not in actual_text.lower():
                    raise AssertionError(f"Text '{expected_text}' not found in '{actual_text}'")
            log.info(f"Element {selector} contains text '{expected_text}' as expected")
        except AssertionError as e:
            error_msg = message or f"Element {selector} should contain text '{expected_text}'"
            log.error(error_msg)
            raise AssertionError(error_msg) from e
    
    def assert_element_has_exact_text(
        self,
        selector: str,
        expected_text: str,
        timeout: int = 10000,
        message: Optional[str] = None
    ):
        """Assert element has exact text."""
        try:
            locator = self.page.locator(selector)
            expect(locator).to_have_text(expected_text, timeout=timeout)
            log.info(f"Element {selector} has exact text '{expected_text}' as expected")
        except AssertionError as e:
            error_msg = message or f"Element {selector} should have exact text '{expected_text}'"
            log.error(error_msg)
            raise AssertionError(error_msg) from e
    
    def assert_element_has_attribute(
        self,
        selector: str,
        attribute: str,
        expected_value: str,
        timeout: int = 10000,
        message: Optional[str] = None
    ):
        """Assert element has specific attribute value."""
        try:
            locator = self.page.locator(selector)
            expect(locator).to_have_attribute(attribute, expected_value, timeout=timeout)
            log.info(f"Element {selector} has attribute {attribute}='{expected_value}' as expected")
        except AssertionError as e:
            error_msg = message or f"Element {selector} should have attribute {attribute}='{expected_value}'"
            log.error(error_msg)
            raise AssertionError(error_msg) from e
    
    def assert_element_count(
        self,
        selector: str,
        expected_count: int,
        timeout: int = 10000,
        message: Optional[str] = None
    ):
        """Assert specific number of elements exist."""
        try:
            locator = self.page.locator(selector)
            expect(locator).to_have_count(expected_count, timeout=timeout)
            log.info(f"Found {expected_count} elements with selector {selector} as expected")
        except AssertionError as e:
            error_msg = message or f"Expected {expected_count} elements with selector {selector}"
            log.error(error_msg)
            raise AssertionError(error_msg) from e
    
    def assert_url_contains(
        self,
        expected_url_part: str,
        timeout: int = 10000,
        message: Optional[str] = None
    ):
        """Assert current URL contains expected part."""
        try:
            self.page.wait_for_url(f"*{expected_url_part}*", timeout=timeout)
            log.info(f"URL contains '{expected_url_part}' as expected")
        except AssertionError as e:
            actual_url = self.page.url
            error_msg = message or f"URL should contain '{expected_url_part}' but is '{actual_url}'"
            log.error(error_msg)
            raise AssertionError(error_msg) from e
    
    def assert_url_equals(
        self,
        expected_url: str,
        timeout: int = 10000,
        message: Optional[str] = None
    ):
        """Assert current URL equals expected URL."""
        try:
            self.page.wait_for_url(expected_url, timeout=timeout)
            log.info(f"URL equals '{expected_url}' as expected")
        except AssertionError as e:
            actual_url = self.page.url
            error_msg = message or f"URL should be '{expected_url}' but is '{actual_url}'"
            log.error(error_msg)
            raise AssertionError(error_msg) from e
    
    def assert_page_title_contains(
        self,
        expected_title_part: str,
        timeout: int = 10000,
        message: Optional[str] = None
    ):
        """Assert page title contains expected part."""
        try:
            title = self.page.title()
            assert expected_title_part in title, f"Title '{title}' does not contain '{expected_title_part}'"
            log.info(f"Page title contains '{expected_title_part}' as expected")
        except AssertionError as e:
            actual_title = self.page.title()
            error_msg = message or f"Page title should contain '{expected_title_part}' but is '{actual_title}'"
            log.error(error_msg)
            raise AssertionError(error_msg) from e
    
    def assert_element_value_equals(
        self,
        selector: str,
        expected_value: str,
        timeout: int = 10000,
        message: Optional[str] = None
    ):
        """Assert input element has specific value."""
        try:
            locator = self.page.locator(selector)
            expect(locator).to_have_value(expected_value, timeout=timeout)
            log.info(f"Element {selector} has value '{expected_value}' as expected")
        except AssertionError as e:
            actual_value = self.page.locator(selector).input_value()
            error_msg = message or f"Element {selector} should have value '{expected_value}' but has '{actual_value}'"
            log.error(error_msg)
            raise AssertionError(error_msg) from e
    
    def assert_element_is_checked(
        self,
        selector: str,
        timeout: int = 10000,
        message: Optional[str] = None
    ):
        """Assert checkbox is checked."""
        try:
            locator = self.page.locator(selector)
            expect(locator).to_be_checked(timeout=timeout)
            log.info(f"Element {selector} is checked as expected")
        except AssertionError as e:
            error_msg = message or f"Element {selector} should be checked but is not"
            log.error(error_msg)
            raise AssertionError(error_msg) from e
    
    def assert_element_is_not_checked(
        self,
        selector: str,
        timeout: int = 10000,
        message: Optional[str] = None
    ):
        """Assert checkbox is not checked."""
        try:
            locator = self.page.locator(selector)
            expect(locator).not_to_be_checked(timeout=timeout)
            log.info(f"Element {selector} is not checked as expected")
        except AssertionError as e:
            error_msg = message or f"Element {selector} should not be checked but is"
            log.error(error_msg)
            raise AssertionError(error_msg) from e
    
    def assert_element_is_focused(
        self,
        selector: str,
        timeout: int = 10000,
        message: Optional[str] = None
    ):
        """Assert element has focus."""
        try:
            locator = self.page.locator(selector)
            expect(locator).to_be_focused(timeout=timeout)
            log.info(f"Element {selector} has focus as expected")
        except AssertionError as e:
            error_msg = message or f"Element {selector} should have focus but does not"
            log.error(error_msg)
            raise AssertionError(error_msg) from e
    
    def assert_css_property_equals(
        self,
        selector: str,
        property_name: str,
        expected_value: str,
        timeout: int = 10000,
        message: Optional[str] = None
    ):
        """Assert element has specific CSS property value."""
        try:
            locator = self.page.locator(selector)
            actual_value = locator.get_attribute("style", timeout=timeout)
            # Parse CSS properties
            css_match = re.search(f"{property_name}:\\s*([^;]+)", actual_value or "")
            if css_match:
                actual_property_value = css_match.group(1).strip()
                assert actual_property_value == expected_value, \
                    f"CSS property {property_name} should be '{expected_value}' but is '{actual_property_value}'"
            else:
                assert False, f"CSS property {property_name} not found in element {selector}"
            
            log.info(f"Element {selector} has CSS property {property_name}='{expected_value}' as expected")
        except AssertionError as e:
            error_msg = message or f"Element {selector} should have CSS property {property_name}='{expected_value}'"
            log.error(error_msg)
            raise AssertionError(error_msg) from e
    
    def assert_element_is_clickable(
        self,
        selector: str,
        timeout: int = 10000,
        message: Optional[str] = None
    ):
        """Assert element is clickable (visible and enabled)."""
        try:
            locator = self.page.locator(selector)
            expect(locator).to_be_visible(timeout=timeout)
            expect(locator).to_be_enabled(timeout=timeout)
            log.info(f"Element {selector} is clickable as expected")
        except AssertionError as e:
            error_msg = message or f"Element {selector} should be clickable but is not"
            log.error(error_msg)
            raise AssertionError(error_msg) from e
    
    def assert_text_matches_regex(
        self,
        selector: str,
        regex_pattern: str,
        timeout: int = 10000,
        message: Optional[str] = None
    ):
        """Assert element text matches regex pattern."""
        try:
            locator = self.page.locator(selector)
            text = locator.text_content(timeout=timeout)
            pattern = re.compile(regex_pattern)
            assert pattern.search(text), f"Text '{text}' does not match pattern '{regex_pattern}'"
            log.info(f"Element {selector} text matches regex pattern '{regex_pattern}' as expected")
        except AssertionError as e:
            actual_text = self.page.locator(selector).text_content(timeout=timeout)
            error_msg = message or f"Element {selector} text should match regex '{regex_pattern}' but is '{actual_text}'"
            log.error(error_msg)
            raise AssertionError(error_msg) from e
    
    def assert_element_is_within_viewport(
        self,
        selector: str,
        timeout: int = 10000,
        message: Optional[str] = None
    ):
        """Assert element is within viewport."""
        try:
            locator = self.page.locator(selector)
            bounding_box = locator.bounding_box(timeout=timeout)
            viewport_size = self.page.viewport_size
            
            assert bounding_box is not None, f"Element {selector} not found"
            assert bounding_box['x'] >= 0, f"Element {selector} is outside left viewport"
            assert bounding_box['y'] >= 0, f"Element {selector} is outside top viewport"
            assert bounding_box['x'] + bounding_box['width'] <= viewport_size['width'], \
                f"Element {selector} is outside right viewport"
            assert bounding_box['y'] + bounding_box['height'] <= viewport_size['height'], \
                f"Element {selector} is outside bottom viewport"
            
            log.info(f"Element {selector} is within viewport as expected")
        except AssertionError as e:
            error_msg = message or f"Element {selector} should be within viewport but is not"
            log.error(error_msg)
            raise AssertionError(error_msg) from e
    
    def assert_api_response_contains(
        self,
        response_data: Dict[str, Any],
        expected_key: str,
        expected_value: Any,
        message: Optional[str] = None
    ):
        """Assert API response contains expected key-value pair."""
        try:
            assert expected_key in response_data, f"Key '{expected_key}' not found in response"
            assert response_data[expected_key] == expected_value, \
                f"Value for key '{expected_key}' should be '{expected_value}' but is '{response_data[expected_key]}'"
            log.info(f"API response contains {expected_key}='{expected_value}' as expected")
        except AssertionError as e:
            error_msg = message or f"API response should contain {expected_key}='{expected_value}'"
            log.error(error_msg)
            raise AssertionError(error_msg) from e
    
    def assert_json_schema_valid(
        self,
        json_data: Dict[str, Any],
        expected_schema: Dict[str, Any],
        message: Optional[str] = None
    ):
        """Assert JSON data matches expected schema (basic validation)."""
        try:
            # Basic schema validation - can be enhanced with jsonschema library
            for key, expected_type in expected_schema.items():
                assert key in json_data, f"Required key '{key}' missing from JSON"
                
                if expected_type == "string":
                    assert isinstance(json_data[key], str), f"Key '{key}' should be string"
                elif expected_type == "number":
                    assert isinstance(json_data[key], (int, float)), f"Key '{key}' should be number"
                elif expected_type == "boolean":
                    assert isinstance(json_data[key], bool), f"Key '{key}' should be boolean"
                elif expected_type == "array":
                    assert isinstance(json_data[key], list), f"Key '{key}' should be array"
                elif expected_type == "object":
                    assert isinstance(json_data[key], dict), f"Key '{key}' should be object"
            
            log.info("JSON schema validation passed")
        except AssertionError as e:
            error_msg = message or f"JSON schema validation failed"
            log.error(error_msg)
            raise AssertionError(error_msg) from e


def create_assertion_helper(page: Page) -> AssertionHelper:
    """
    Factory function to create AssertionHelper instance.
    
    Args:
        page: Playwright page instance
        
    Returns:
        AssertionHelper instance
    """
    return AssertionHelper(page)
