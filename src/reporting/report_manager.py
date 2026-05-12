"""Centralized reporting manager for enterprise test framework."""
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from playwright.sync_api import Page
from src.config.settings import get_settings
from src.config.logger import log
from src.reporting.allure_reporter import AllureReporter, get_allure_reporter
from src.reporting.html_reporter import HTMLReporter, get_html_reporter
from src.utils.screenshot_manager import ScreenshotManager


class ReportManager:
    """Centralized reporting manager coordinating all reporting systems."""
    
    def __init__(self, page: Optional[Page] = None):
        """Initialize report manager.
        
        Args:
            page: Playwright page instance
        """
        self.settings = get_settings()
        self.page = page
        self.allure_reporter = get_allure_reporter(page)
        self.html_reporter = get_html_reporter()
        self.screenshot_manager = ScreenshotManager(page) if page else None
        self.current_test_data = {}
        self.execution_session = {
            'session_id': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'start_time': datetime.now().isoformat(),
            'tests': [],
            'environment': self.settings.test_env.value,
            'browser': self.settings.browser.value
        }
    
    def start_test_reporting(
        self,
        test_name: str,
        test_id: str,
        suite: Optional[str] = None,
        epic: Optional[str] = None,
        feature: Optional[str] = None,
        story: Optional[str] = None,
        severity: str = "normal",
        tags: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start comprehensive test reporting.
        
        Args:
            test_name: Test name
            test_id: Test identifier
            suite: Test suite name
            epic: Test epic
            feature: Test feature
            story: Test story
            severity: Test severity
            tags: Test tags
            description: Test description
            
        Returns:
            Test data dictionary
        """
        try:
            # Initialize test data
            self.current_test_data = {
                'test_name': test_name,
                'test_id': test_id,
                'suite': suite,
                'epic': epic,
                'feature': feature,
                'story': story,
                'severity': severity,
                'tags': tags or [],
                'description': description,
                'start_time': datetime.now().isoformat(),
                'status': 'running',
                'attachments': [],
                'performance_metrics': {},
                'metadata': {
                    'environment': self.settings.test_env.value,
                    'browser': self.settings.browser.value,
                    'headless': self.settings.headless,
                    'viewport': f"{self.settings.window_width}x{self.settings.window_height}"
                }
            }
            
            # Configure Allure reporting
            self.allure_reporter.start_test(test_name, test_id)
            self.allure_reporter.add_environment_info()
            
            if epic:
                self.allure_reporter.add_test_epic(epic)
            if feature:
                self.allure_reporter.add_test_feature(feature)
            if story:
                self.allure_reporter.add_test_story(story)
            if severity:
                self.allure_reporter.add_test_severity(severity)
            if tags:
                self.allure_reporter.add_test_tags(tags)
            if description:
                self.allure_reporter.add_test_description(description)
            
            log.info(f"Started reporting for test: {test_name}")
            return self.current_test_data
            
        except Exception as e:
            log.error(f"Failed to start test reporting: {e}")
            return {}
    
    def add_test_step(self, step_name: str, description: Optional[str] = None):
        """Add test step to reports.
        
        Args:
            step_name: Step name
            description: Step description
        """
        try:
            # Add to Allure
            allure_step = self.allure_reporter.add_test_step(step_name, description)
            if allure_step:
                return allure_step
            
            # Add to test data
            if 'steps' not in self.current_test_data:
                self.current_test_data['steps'] = []
            
            self.current_test_data['steps'].append({
                'name': step_name,
                'description': description,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            log.error(f"Failed to add test step: {e}")
    
    def attach_screenshot(self, name: str, description: Optional[str] = None):
        """Attach screenshot to all reports.
        
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
                self.allure_reporter.attach_screenshot(name, description)
                
                # Add to test data
                attachment = {
                    'type': 'screenshot',
                    'name': name,
                    'path': screenshot_path,
                    'description': description,
                    'timestamp': datetime.now().isoformat()
                }
                self.current_test_data['attachments'].append(attachment)
                
                log.info(f"Screenshot attached: {screenshot_path}")
            else:
                log.warning(f"Failed to capture screenshot: {screenshot_path}")
                
        except Exception as e:
            log.error(f"Failed to attach screenshot: {e}")
    
    def attach_failure_screenshot(self, error_message: str):
        """Attach failure screenshot with context.
        
        Args:
            error_message: Error message
        """
        try:
            test_name = self.current_test_data.get('test_name', 'unknown_test')
            
            # Attach to Allure
            self.allure_reporter.attach_failure_screenshot(test_name, error_message)
            
            # Add to test data
            attachment = {
                'type': 'failure_screenshot',
                'name': f"Failure - {test_name}",
                'error_message': error_message,
                'timestamp': datetime.now().isoformat()
            }
            self.current_test_data['attachments'].append(attachment)
            
            log.info(f"Failure screenshot attached for: {test_name}")
            
        except Exception as e:
            log.error(f"Failed to attach failure screenshot: {e}")
    
    def attach_performance_metrics(self, metrics: Dict[str, float]):
        """Attach performance metrics to reports.
        
        Args:
            metrics: Performance metrics dictionary
        """
        try:
            # Add to Allure
            self.allure_reporter.add_performance_metrics(metrics)
            
            # Add to test data
            self.current_test_data['performance_metrics'] = metrics
            
            log.info("Performance metrics attached to reports")
            
        except Exception as e:
            log.error(f"Failed to attach performance metrics: {e}")
    
    def attach_json_data(self, data: Dict[str, Any], name: str = "Test Data"):
        """Attach JSON data to reports.
        
        Args:
            data: JSON data
            name: Attachment name
        """
        try:
            # Add to Allure
            self.allure_reporter.attach_json_data(data, name)
            
            # Add to test data
            attachment = {
                'type': 'json',
                'name': name,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            self.current_test_data['attachments'].append(attachment)
            
            log.info(f"JSON data attached: {name}")
            
        except Exception as e:
            log.error(f"Failed to attach JSON data: {e}")
    
    def mark_test_passed(self, message: str = "Test passed successfully"):
        """Mark test as passed in all reports.
        
        Args:
            message: Success message
        """
        try:
            # Update test data
            self.current_test_data['status'] = 'passed'
            self.current_test_data['end_time'] = datetime.now().isoformat()
            self.current_test_data['duration'] = self._calculate_duration()
            self.current_test_data['message'] = message
            
            # Mark in Allure
            self.allure_reporter.mark_test_passed(message)
            
            # Add to HTML reporter
            self.html_reporter.add_test_result(self.current_test_data.copy())
            
            # Add to session
            self.execution_session['tests'].append(self.current_test_data.copy())
            
            log.info(f"Test marked as passed: {message}")
            
        except Exception as e:
            log.error(f"Failed to mark test as passed: {e}")
    
    def mark_test_failed(self, error: Exception, message: Optional[str] = None):
        """Mark test as failed in all reports.
        
        Args:
            error: Exception that caused failure
            message: Optional failure message
        """
        try:
            # Update test data
            self.current_test_data['status'] = 'failed'
            self.current_test_data['end_time'] = datetime.now().isoformat()
            self.current_test_data['duration'] = self._calculate_duration()
            self.current_test_data['error_message'] = str(error)
            self.current_test_data['error_type'] = type(error).__name__
            self.current_test_data['message'] = message or str(error)
            
            # Attach failure screenshot
            self.attach_failure_screenshot(str(error))
            
            # Mark in Allure
            self.allure_reporter.mark_test_failed(error, message)
            
            # Add to HTML reporter
            self.html_reporter.add_test_result(self.current_test_data.copy())
            
            # Add to session
            self.execution_session['tests'].append(self.current_test_data.copy())
            
            log.error(f"Test marked as failed: {error}")
            
        except Exception as e:
            log.error(f"Failed to mark test as failed: {e}")
    
    def mark_test_skipped(self, reason: str):
        """Mark test as skipped in all reports.
        
        Args:
            reason: Skip reason
        """
        try:
            # Update test data
            self.current_test_data['status'] = 'skipped'
            self.current_test_data['end_time'] = datetime.now().isoformat()
            self.current_test_data['duration'] = self._calculate_duration()
            self.current_test_data['skip_reason'] = reason
            
            # Mark in Allure
            self.allure_reporter.mark_test_skipped(reason)
            
            # Add to HTML reporter
            self.html_reporter.add_test_result(self.current_test_data.copy())
            
            # Add to session
            self.execution_session['tests'].append(self.current_test_data.copy())
            
            log.info(f"Test marked as skipped: {reason}")
            
        except Exception as e:
            log.error(f"Failed to mark test as skipped: {e}")
    
    def _calculate_duration(self) -> float:
        """Calculate test duration.
        
        Returns:
            Duration in seconds
        """
        try:
            if 'start_time' in self.current_test_data and 'end_time' in self.current_test_data:
                start = datetime.fromisoformat(self.current_test_data['start_time'])
                end = datetime.fromisoformat(self.current_test_data['end_time'])
                return (end - start).total_seconds()
            return 0.0
        except Exception:
            return 0.0
    
    def finalize_session(self) -> Dict[str, str]:
        """Generate all reports for the session.
        
        Returns:
            Dictionary of generated report paths
        """
        try:
            # Update session end time
            self.execution_session['end_time'] = datetime.now().isoformat()
            
            # Generate HTML reports
            html_reports = self.html_reporter.generate_all_reports()
            
            # Generate session summary
            session_report_path = self._save_session_summary()
            
            # Generate Allure command
            allure_command = self._generate_allure_command()
            
            reports = {
                **html_reports,
                'session_summary': session_report_path,
                'allure_command': allure_command
            }
            
            log.info(f"Session finalized with {len(reports)} reports")
            return reports
            
        except Exception as e:
            log.error(f"Failed to finalize session: {e}")
            return {}
    
    def _save_session_summary(self) -> str:
        """Save session summary to JSON.
        
        Returns:
            Path to saved summary
        """
        try:
            reports_dir = Path(self.settings.html_report_dir)
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            summary_file = reports_dir / f"session_{self.execution_session['session_id']}.json"
            
            with open(summary_file, 'w') as f:
                json.dump(self.execution_session, f, indent=2, default=str)
            
            log.info(f"Session summary saved: {summary_file}")
            return str(summary_file)
            
        except Exception as e:
            log.error(f"Failed to save session summary: {e}")
            return ""
    
    def _generate_allure_command(self) -> str:
        """Generate Allure report generation command.
        
        Returns:
            Allure command string
        """
        try:
            allure_dir = Path(self.settings.allure_report_dir)
            output_dir = allure_dir / "report"
            
            command = f"allure generate {allure_dir} --clean -o {output_dir}"
            
            log.info(f"Allure command generated: {command}")
            return command
            
        except Exception as e:
            log.error(f"Failed to generate Allure command: {e}")
            return ""
    
    def get_test_execution_summary(self) -> Dict[str, Any]:
        """Get current test execution summary.
        
        Returns:
            Execution summary dictionary
        """
        try:
            total_tests = len(self.execution_session['tests'])
            passed_tests = len([t for t in self.execution_session['tests'] if t.get('status') == 'passed'])
            failed_tests = len([t for t in self.execution_session['tests'] if t.get('status') == 'failed'])
            skipped_tests = len([t for t in self.execution_session['tests'] if t.get('status') == 'skipped'])
            
            total_duration = sum(t.get('duration', 0.0) for t in self.execution_session['tests'])
            pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0.0
            
            return {
                'session_id': self.execution_session['session_id'],
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'skipped': skipped_tests,
                'pass_rate': pass_rate,
                'total_duration': total_duration,
                'environment': self.execution_session['environment'],
                'browser': self.execution_session['browser'],
                'start_time': self.execution_session['start_time'],
                'current_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            log.error(f"Failed to get execution summary: {e}")
            return {}
    
    def cleanup_old_reports(self, days_to_keep: int = 7):
        """Clean up old report files.
        
        Args:
            days_to_keep: Number of days to keep reports
        """
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            
            # Clean HTML reports
            html_dir = Path(self.settings.html_report_dir)
            if html_dir.exists():
                for file_path in html_dir.rglob('*'):
                    if file_path.is_file() and file_path.stat().st_mtime < cutoff_date:
                        file_path.unlink()
                        log.debug(f"Cleaned old report: {file_path}")
            
            # Clean Allure reports
            allure_dir = Path(self.settings.allure_report_dir)
            if allure_dir.exists():
                for file_path in allure_dir.rglob('*'):
                    if file_path.is_file() and file_path.stat().st_mtime < cutoff_date:
                        file_path.unlink()
                        log.debug(f"Cleaned old Allure result: {file_path}")
            
            log.info(f"Cleaned reports older than {days_to_keep} days")
            
        except Exception as e:
            log.error(f"Failed to cleanup old reports: {e}")


# Global report manager instance
_report_manager = None


def get_report_manager(page: Optional[Page] = None) -> ReportManager:
    """Get global report manager instance.
    
    Args:
        page: Playwright page instance
        
    Returns:
        ReportManager instance
    """
    global _report_manager
    
    if _report_manager is None or (page and _report_manager.page != page):
        _report_manager = ReportManager(page)
    
    return _report_manager


def setup_test_reporting(
    page: Page,
    test_name: str,
    test_id: str,
    **kwargs
) -> ReportManager:
    """Setup comprehensive test reporting.
    
    Args:
        page: Playwright page instance
        test_name: Test name
        test_id: Test identifier
        **kwargs: Additional test metadata
        
    Returns:
        Configured ReportManager instance
    """
    manager = get_report_manager(page)
    manager.start_test_reporting(test_name, test_id, **kwargs)
    return manager


def finalize_test_reporting() -> Dict[str, str]:
    """Finalize all test reporting.
    
    Returns:
        Dictionary of generated report paths
    """
    manager = get_report_manager()
    return manager.finalize_session()


# Decorators for easy integration
def report_test(
    epic: Optional[str] = None,
    feature: Optional[str] = None,
    story: Optional[str] = None,
    severity: str = "normal",
    tags: Optional[List[str]] = None,
    description: Optional[str] = None,
    suite: Optional[str] = None
):
    """Decorator for automatic test reporting.
    
    Args:
        epic: Test epic
        feature: Test feature
        story: Test story
        severity: Test severity
        tags: Test tags
        description: Test description
        suite: Test suite
    """
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            try:
                # Extract page from arguments if available
                page = None
                for arg in args:
                    if hasattr(arg, 'goto'):  # Check if it's a Page object
                        page = arg
                        break
                
                # Setup reporting
                test_name = f"{test_func.__module__}.{test_func.__name__}"
                test_id = f"{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                manager = get_report_manager(page)
                manager.start_test_reporting(
                    test_name=test_name,
                    test_id=test_id,
                    suite=suite,
                    epic=epic,
                    feature=feature,
                    story=story,
                    severity=severity,
                    tags=tags,
                    description=description
                )
                
                # Execute test
                try:
                    result = test_func(*args, **kwargs)
                    manager.mark_test_passed()
                    return result
                except Exception as e:
                    manager.mark_test_failed(e)
                    raise
                except pytest.skip.Exception as e:
                    manager.mark_test_skipped(str(e))
                    raise
                    
            except Exception as e:
                log.error(f"Test reporting decorator failed: {e}")
                # Execute test without reporting
                return test_func(*args, **kwargs)
        
        return wrapper
    return decorator
