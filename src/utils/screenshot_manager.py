"""Advanced screenshot and media management for test documentation."""
import os
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from playwright.sync_api import Page, BrowserContext
from src.config.settings import get_settings
from src.config.logger import log


class ScreenshotManager:
    """Advanced screenshot management with automatic organization."""
    
    def __init__(self, page: Page, context: Optional[BrowserContext] = None):
        """Initialize screenshot manager."""
        self.page = page
        self.context = context
        self.settings = get_settings()
        self.screenshot_dir = Path("reports/screenshots")
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure screenshot directories exist."""
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for organization
        for subdir in ['failures', 'success', 'debug', 'before', 'after']:
            (self.screenshot_dir / subdir).mkdir(exist_ok=True)
    
    def generate_filename(
        self,
        test_name: str,
        step: Optional[str] = None,
        status: str = "debug",
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Generate unique filename for screenshot.
        
        Args:
            test_name: Name of the test
            step: Test step description
            status: Status (success, failure, debug, before, after)
            timestamp: Custom timestamp
            
        Returns:
            Generated filename
        """
        timestamp = timestamp or datetime.now()
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S_%f")[:-3]
        
        # Clean test name for filename
        clean_test_name = "".join(c for c in test_name if c.isalnum() or c in ('_', '-')).rstrip()
        
        if step:
            clean_step = "".join(c for c in step if c.isalnum() or c in ('_', '-')).rstrip()
            filename = f"{timestamp_str}_{clean_test_name}_{clean_step}_{status}.png"
        else:
            filename = f"{timestamp_str}_{clean_test_name}_{status}.png"
        
        return filename
    
    def take_screenshot(
        self,
        test_name: str,
        step: Optional[str] = None,
        status: str = "debug",
        full_page: bool = True,
        quality: Optional[int] = None,
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Take screenshot with automatic organization.
        
        Args:
            test_name: Name of the test
            step: Test step description
            status: Status for organization
            full_page: Capture full page
            quality: Image quality (1-100)
            timestamp: Custom timestamp
            
        Returns:
            Path to saved screenshot
        """
        try:
            filename = self.generate_filename(test_name, step, status, timestamp)
            
            # Determine subdirectory based on status
            if status in ['failure', 'fail', 'error']:
                subdir = 'failures'
            elif status in ['success', 'pass']:
                subdir = 'success'
            elif status in ['before', 'after']:
                subdir = status
            else:
                subdir = 'debug'
            
            filepath = self.screenshot_dir / subdir / filename
            
            # Take screenshot
            screenshot_options = {
                'path': str(filepath),
                'full_page': full_page
            }
            
            if quality is not None:
                screenshot_options['quality'] = quality
            
            self.page.screenshot(**screenshot_options)
            
            log.info(f"Screenshot saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            log.error(f"Failed to take screenshot: {e}")
            raise
    
    def take_failure_screenshot(
        self,
        test_name: str,
        error_message: Optional[str] = None,
        full_page: bool = True
    ) -> str:
        """
        Take screenshot specifically for test failures.
        
        Args:
            test_name: Name of the failing test
            error_message: Error message to include in filename
            full_page: Capture full page
            
        Returns:
            Path to saved screenshot
        """
        step = f"failure_{error_message[:50]}" if error_message else "failure"
        return self.take_screenshot(
            test_name=test_name,
            step=step,
            status="failure",
            full_page=full_page
        )
    
    def take_before_after_screenshots(
        self,
        test_name: str,
        action_name: str,
        before: bool = True,
        after: bool = True
    ) -> Dict[str, str]:
        """
        Take before and after screenshots for an action.
        
        Args:
            test_name: Name of the test
            action_name: Description of the action
            before: Take before screenshot
            after: Take after screenshot
            
        Returns:
            Dictionary with paths to screenshots
        """
        screenshots = {}
        
        if before:
            before_path = self.take_screenshot(
                test_name=test_name,
                step=f"before_{action_name}",
                status="before"
            )
            screenshots['before'] = before_path
        
        # Action would be performed here
        
        if after:
            after_path = self.take_screenshot(
                test_name=test_name,
                step=f"after_{action_name}",
                status="after"
            )
            screenshots['after'] = after_path
        
        return screenshots
    
    def capture_element_screenshot(
        self,
        selector: str,
        test_name: str,
        step: Optional[str] = None
    ) -> str:
        """
        Capture screenshot of specific element.
        
        Args:
            selector: CSS selector for element
            test_name: Name of the test
            step: Test step description
            
        Returns:
            Path to saved screenshot
        """
        try:
            filename = self.generate_filename(test_name, step, "element")
            filepath = self.screenshot_dir / "elements" / filename
            
            # Create elements directory
            (self.screenshot_dir / "elements").mkdir(exist_ok=True)
            
            # Take element screenshot
            element = self.page.locator(selector)
            element.screenshot(path=str(filepath))
            
            log.info(f"Element screenshot saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            log.error(f"Failed to capture element screenshot: {e}")
            raise
    
    def get_screenshot_as_base64(
        self,
        selector: Optional[str] = None,
        full_page: bool = False
    ) -> str:
        """
        Get screenshot as base64 string for embedding in reports.
        
        Args:
            selector: CSS selector for element (None for full page)
            full_page: Capture full page
            
        Returns:
            Base64 encoded screenshot
        """
        try:
            if selector:
                element = self.page.locator(selector)
                screenshot_bytes = element.screenshot()
            else:
                screenshot_bytes = self.page.screenshot(full_page=full_page)
            
            return base64.b64encode(screenshot_bytes).decode('utf-8')
            
        except Exception as e:
            log.error(f"Failed to get screenshot as base64: {e}")
            raise
    
    def create_screenshot_gallery(
        self,
        test_name: str,
        screenshots: List[str],
        gallery_name: Optional[str] = None
    ) -> str:
        """
        Create HTML gallery from multiple screenshots.
        
        Args:
            test_name: Name of the test
            screenshots: List of screenshot paths
            gallery_name: Name for the gallery
            
        Returns:
            Path to HTML gallery file
        """
        try:
            gallery_name = gallery_name or f"{test_name}_gallery"
            filename = f"{gallery_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            filepath = self.screenshot_dir / "galleries" / filename
            
            # Create galleries directory
            (self.screenshot_dir / "galleries").mkdir(exist_ok=True)
            
            # Generate HTML gallery
            html_content = self._generate_gallery_html(gallery_name, screenshots)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            log.info(f"Screenshot gallery created: {filepath}")
            return str(filepath)
            
        except Exception as e:
            log.error(f"Failed to create screenshot gallery: {e}")
            raise
    
    def _generate_gallery_html(self, title: str, screenshots: List[str]) -> str:
        """Generate HTML content for screenshot gallery."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .gallery {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }}
                .screenshot {{ border: 1px solid #ddd; border-radius: 5px; overflow: hidden; }}
                .screenshot img {{ width: 100%; height: auto; }}
                .screenshot-caption {{ padding: 10px; background: #f5f5f5; font-size: 12px; }}
                h1 {{ color: #333; text-align: center; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <div class="gallery">
        """
        
        for screenshot_path in screenshots:
            screenshot_name = Path(screenshot_path).name
            html += f"""
                <div class="screenshot">
                    <img src="{screenshot_name}" alt="{screenshot_name}">
                    <div class="screenshot-caption">{screenshot_name}</div>
                </div>
            """
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html
    
    def cleanup_old_screenshots(self, days_to_keep: int = 7):
        """
        Clean up old screenshots based on retention policy.
        
        Args:
            days_to_keep: Number of days to keep screenshots
        """
        try:
            cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            
            for root, dirs, files in os.walk(self.screenshot_dir):
                for file in files:
                    file_path = Path(root) / file
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        log.info(f"Deleted old screenshot: {file_path}")
            
        except Exception as e:
            log.error(f"Failed to cleanup old screenshots: {e}")


def create_screenshot_manager(page: Page, context: Optional[BrowserContext] = None) -> ScreenshotManager:
    """
    Factory function to create ScreenshotManager instance.
    
    Args:
        page: Playwright page instance
        context: Browser context instance
        
    Returns:
        ScreenshotManager instance
    """
    return ScreenshotManager(page, context)
