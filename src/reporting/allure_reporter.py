"""Advanced Allure reporting integration for enterprise test framework."""
import os
import json
import allure
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from playwright.sync_api import Page
from src.config.settings import get_settings
from src.config.logger import log
from src.utils.screenshot_manager import ScreenshotManager


class AllureReporter:
    """Enterprise-grade Allure reporting integration."""
    
    def __init__(self, page: Optional[Page] = None):
        """Initialize Allure reporter.
        
        Args:
            page: Playwright page instance for screenshots
        """
        self.page = page
        self.settings = get_settings()
        self.screenshot_manager = ScreenshotManager(page) if page else None
        self.test_data = {}
        self.attachments = []
    
    def start_test(self, test_name: str, test_id: str):
        """Start Allure test reporting.
        
        Args:
            test_name: Name of the test
            test_id: Unique test identifier
        """
        try:
            allure.dynamic.title(test_name)
            allure.dynamic.testcase(test_id)
            
            # Add test metadata
            self.test_data['test_name'] = test_name
            self.test_data['test_id'] = test_id
            self.test_data['start_time'] = datetime.now().isoformat()
            
            log.info(f"Allure reporting started for: {test_name}")
            
        except Exception as e:
            log.error(f"Failed to start Allure reporting: {e}")
    
    def add_environment_info(self):
        """Add environment information to Allure report."""
        try:
            environment_data = {
                'Environment': self.settings.test_env.value,
                'Base URL': self.settings.base_url,
                'Browser': self.settings.browser.value,
                'Headless': str(self.settings.headless),
                'Window Size': f"{self.settings.window_width}x{self.settings.window_height}",
                'Timeout': str(self.settings.explicit_wait),
                'Test Execution Time': datetime.now().isoformat(),
                'Python Version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
                'Platform': os.name
            }
            
            allure.dynamic.parameter('Environment', self.settings.test_env.value)
            allure.dynamic.parameter('Browser', self.settings.browser.value)
            allure.dynamic.parameter('Platform', os.name)
            
            # Add environment properties file
            allure_dir = Path(self.settings.allure_report_dir)
            allure_dir.mkdir(parents=True, exist_ok=True)
            
            env_file = allure_dir / "environment.properties"
            with open(env_file, 'w') as f:
                for key, value in environment_data.items():
                    f.write(f"{key}={value}\n")
            
            log.info("Environment information added to Allure report")
            
        except Exception as e:
            log.error(f"Failed to add environment info: {e}")
    
    def add_test_description(self, description: str):
        """Add test description to Allure report.
        
        Args:
            description: Test description
        """
        try:
            allure.dynamic.description(description)
            self.test_data['description'] = description
        except Exception as e:
            log.error(f"Failed to add test description: {e}")
    
    def add_test_tags(self, tags: List[str]):
        """Add tags to Allure test.
        
        Args:
            tags: List of tags
        """
        try:
            for tag in tags:
                allure.dynamic.tag(tag)
            self.test_data['tags'] = tags
        except Exception as e:
            log.error(f"Failed to add test tags: {e}")
    
    def add_test_severity(self, severity: str):
        """Add test severity to Allure report.
        
        Args:
            severity: Test severity (blocker, critical, normal, minor)
        """
        try:
            severity_map = {
                'blocker': allure.severity_level.BLOCKER,
                'critical': allure.severity_level.CRITICAL,
                'normal': allure.severity_level.NORMAL,
                'minor': allure.severity_level.MINOR,
                'trivial': allure.severity_level.TRIVIAL
            }
            
            if severity.lower() in severity_map:
                allure.dynamic.severity(severity_map[severity.lower()])
                self.test_data['severity'] = severity
        except Exception as e:
            log.error(f"Failed to add test severity: {e}")
    
    def add_test_epic(self, epic: str):
        """Add epic to Allure test.
        
        Args:
            epic: Epic name
        """
        try:
            allure.dynamic.epic(epic)
            self.test_data['epic'] = epic
        except Exception as e:
            log.error(f"Failed to add test epic: {e}")
    
    def add_test_feature(self, feature: str):
        """Add feature to Allure test.
        
        Args:
            feature: Feature name
        """
        try:
            allure.dynamic.feature(feature)
            self.test_data['feature'] = feature
        except Exception as e:
            log.error(f"Failed to add test feature: {e}")
    
    def add_test_story(self, story: str):
        """Add story to Allure test.
        
        Args:
            story: Story name
        """
        try:
            allure.dynamic.story(story)
            self.test_data['story'] = story
        except Exception as e:
            log.error(f"Failed to add test story: {e}")
    
    def attach_screenshot(self, name: str, description: Optional[str] = None):
        """Attach screenshot to Allure report.
        
        Args:
            name: Screenshot name
            description: Optional description
        """
        try:
            if not self.screenshot_manager:
                log.warning("No screenshot manager available")
                return
            
            # Take screenshot
            screenshot_path = self.screenshot_manager.take_screenshot(name)
            
            if screenshot_path and Path(screenshot_path).exists():
                # Attach to Allure
                allure.attach.file(
                    screenshot_path,
                    name=name,
                    attachment_type=allure.attachment_type.PNG
                )
                
                self.attachments.append({
                    'type': 'screenshot',
                    'name': name,
                    'path': screenshot_path,
                    'description': description
                })
                
                log.info(f"Screenshot attached to Allure: {screenshot_path}")
            else:
                log.warning(f"Failed to capture screenshot: {screenshot_path}")
                
        except Exception as e:
            log.error(f"Failed to attach screenshot: {e}")
    
    def attach_failure_screenshot(self, test_name: str, error_message: str):
        """Attach failure screenshot with context.
        
        Args:
            test_name: Name of the failed test
            error_message: Error message
        """
        try:
            if not self.screenshot_manager:
                return
            
            # Take failure screenshot
            screenshot_path = self.screenshot_manager.take_failure_screenshot(test_name, error_message)
            
            if screenshot_path and Path(screenshot_path).exists():
                allure.attach.file(
                    screenshot_path,
                    name=f"Failure Screenshot - {test_name}",
                    attachment_type=allure.attachment_type.PNG
                )
                
                self.attachments.append({
                    'type': 'failure_screenshot',
                    'name': f"Failure Screenshot - {test_name}",
                    'path': screenshot_path,
                    'error_message': error_message
                })
                
                log.info(f"Failure screenshot attached: {screenshot_path}")
                
        except Exception as e:
            log.error(f"Failed to attach failure screenshot: {e}")
    
    def attach_html_report(self, html_content: str, name: str = "HTML Report"):
        """Attach HTML content to Allure report.
        
        Args:
            html_content: HTML content to attach
            name: Attachment name
        """
        try:
            allure.attach(
                html_content,
                name=name,
                attachment_type=allure.attachment_type.HTML
            )
            
            self.attachments.append({
                'type': 'html',
                'name': name,
                'content': html_content
            })
            
            log.info(f"HTML content attached: {name}")
            
        except Exception as e:
            log.error(f"Failed to attach HTML content: {e}")
    
    def attach_json_data(self, data: Dict[str, Any], name: str = "Test Data"):
        """Attach JSON data to Allure report.
        
        Args:
            data: JSON data to attach
            name: Attachment name
        """
        try:
            json_content = json.dumps(data, indent=2, default=str)
            allure.attach(
                json_content,
                name=name,
                attachment_type=allure.attachment_type.JSON
            )
            
            self.attachments.append({
                'type': 'json',
                'name': name,
                'data': data
            })
            
            log.info(f"JSON data attached: {name}")
            
        except Exception as e:
            log.error(f"Failed to attach JSON data: {e}")
    
    def attach_text_log(self, log_content: str, name: str = "Test Log"):
        """Attach text log to Allure report.
        
        Args:
            log_content: Log content to attach
            name: Attachment name
        """
        try:
            allure.attach(
                log_content,
                name=name,
                attachment_type=allure.attachment_type.TEXT
            )
            
            self.attachments.append({
                'type': 'text',
                'name': name,
                'content': log_content
            })
            
            log.info(f"Text log attached: {name}")
            
        except Exception as e:
            log.error(f"Failed to attach text log: {e}")
    
    def add_test_step(self, step_name: str, description: Optional[str] = None):
        """Add test step to Allure report.
        
        Args:
            step_name: Step name
            description: Optional description
            
        Returns:
            Allure step context manager
        """
        try:
            if description:
                return allure.step(f"{step_name}: {description}")
            else:
                return allure.step(step_name)
        except Exception as e:
            log.error(f"Failed to add test step: {e}")
            return None
    
    def mark_test_passed(self, message: str = "Test passed successfully"):
        """Mark test as passed in Allure report.
        
        Args:
            message: Success message
        """
        try:
            self.test_data['status'] = 'passed'
            self.test_data['end_time'] = datetime.now().isoformat()
            self.test_data['message'] = message
            
            log.info(f"Test marked as passed: {message}")
            
        except Exception as e:
            log.error(f"Failed to mark test as passed: {e}")
    
    def mark_test_failed(self, error: Exception, message: Optional[str] = None):
        """Mark test as failed in Allure report.
        
        Args:
            error: Exception that caused failure
            message: Optional failure message
        """
        try:
            self.test_data['status'] = 'failed'
            self.test_data['end_time'] = datetime.now().isoformat()
            self.test_data['error'] = str(error)
            self.test_data['message'] = message or str(error)
            
            # Attach failure screenshot if available
            if self.screenshot_manager:
                test_name = self.test_data.get('test_name', 'unknown_test')
                self.attach_failure_screenshot(test_name, str(error))
            
            log.error(f"Test marked as failed: {error}")
            
        except Exception as e:
            log.error(f"Failed to mark test as failed: {e}")
    
    def mark_test_skipped(self, reason: str):
        """Mark test as skipped in Allure report.
        
        Args:
            reason: Skip reason
        """
        try:
            self.test_data['status'] = 'skipped'
            self.test_data['end_time'] = datetime.now().isoformat()
            self.test_data['skip_reason'] = reason
            
            log.info(f"Test marked as skipped: {reason}")
            
        except Exception as e:
            log.error(f"Failed to mark test as skipped: {e}")
    
    def add_performance_metrics(self, metrics: Dict[str, float]):
        """Add performance metrics to Allure report.
        
        Args:
            metrics: Performance metrics dictionary
        """
        try:
            # Add as JSON attachment
            self.attach_json_data(metrics, "Performance Metrics")
            
            # Add as parameters
            for metric_name, value in metrics.items():
                allure.dynamic.parameter(f"Performance - {metric_name}", f"{value:.3f}s")
            
            self.test_data['performance_metrics'] = metrics
            
            log.info("Performance metrics added to Allure report")
            
        except Exception as e:
            log.error(f"Failed to add performance metrics: {e}")
    
    def generate_test_summary(self) -> Dict[str, Any]:
        """Generate comprehensive test summary.
        
        Returns:
            Test summary dictionary
        """
        try:
            summary = {
                'test_data': self.test_data,
                'attachments': self.attachments,
                'execution_time': None,
                'browser_info': {
                    'name': self.settings.browser.value,
                    'headless': self.settings.headless,
                    'viewport': f"{self.settings.window_width}x{self.settings.window_height}"
                }
            }
            
            # Calculate execution time
            if 'start_time' in self.test_data and 'end_time' in self.test_data:
                start = datetime.fromisoformat(self.test_data['start_time'])
                end = datetime.fromisoformat(self.test_data['end_time'])
                summary['execution_time'] = (end - start).total_seconds()
            
            return summary
            
        except Exception as e:
            log.error(f"Failed to generate test summary: {e}")
            return {}
    
    def save_test_artifacts(self, test_name: str):
        """Save test artifacts to reports directory.
        
        Args:
            test_name: Test name for artifact naming
        """
        try:
            artifacts_dir = Path(self.settings.allure_report_dir) / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            
            # Save test summary
            summary = self.generate_test_summary()
            summary_file = artifacts_dir / f"{test_name}_summary.json"
            
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            log.info(f"Test artifacts saved: {summary_file}")
            
        except Exception as e:
            log.error(f"Failed to save test artifacts: {e}")


# Global Allure reporter instance
_allure_reporter = None


def get_allure_reporter(page: Optional[Page] = None) -> AllureReporter:
    """Get global Allure reporter instance.
    
    Args:
        page: Playwright page instance
        
    Returns:
        AllureReporter instance
    """
    global _allure_reporter
    
    if _allure_reporter is None or (page and _allure_reporter.page != page):
        _allure_reporter = AllureReporter(page)
    
    return _allure_reporter


def setup_allure_reporting(page: Page, test_name: str, test_id: str) -> AllureReporter:
    """Setup Allure reporting for a test.
    
    Args:
        page: Playwright page instance
        test_name: Test name
        test_id: Test identifier
        
    Returns:
        Configured AllureReporter instance
    """
    reporter = get_allure_reporter(page)
    reporter.start_test(test_name, test_id)
    reporter.add_environment_info()
    
    return reporter


# Allure decorators for easy integration
def allure_test(
    epic: Optional[str] = None,
    feature: Optional[str] = None,
    story: Optional[str] = None,
    severity: str = "normal",
    tags: Optional[List[str]] = None,
    description: Optional[str] = None
):
    """Decorator for adding Allure metadata to tests.
    
    Args:
        epic: Test epic
        feature: Test feature
        story: Test story
        severity: Test severity
        tags: Test tags
        description: Test description
    """
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            reporter = get_allure_reporter()
            
            if epic:
                reporter.add_test_epic(epic)
            if feature:
                reporter.add_test_feature(feature)
            if story:
                reporter.add_test_story(story)
            if severity:
                reporter.add_test_severity(severity)
            if tags:
                reporter.add_test_tags(tags)
            if description:
                reporter.add_test_description(description)
            
            return test_func(*args, **kwargs)
        
        return wrapper
    return decorator


def allure_step(step_name: str, description: Optional[str] = None):
    """Decorator for adding Allure step to test methods.
    
    Args:
        step_name: Step name
        description: Step description
    """
    def decorator(method):
        def wrapper(*args, **kwargs):
            reporter = get_allure_reporter()
            
            with reporter.add_test_step(step_name, description):
                return method(*args, **kwargs)
        
        return wrapper
    return decorator
