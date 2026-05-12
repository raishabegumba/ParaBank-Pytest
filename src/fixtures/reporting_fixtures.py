"""Enterprise-grade reporting fixtures for test execution."""
import pytest
import os
import json
from datetime import datetime
from typing import Generator, Dict, Any, Optional
from pathlib import Path
from src.config.settings import get_settings
from src.config.logger import log
from src.utils.screenshot_manager import ScreenshotManager


@pytest.fixture(scope="session")
def report_config():
    """
    Report configuration fixture.
    
    Returns:
        Dictionary with report configuration
    """
    settings = get_settings()
    report_paths = settings.get_report_paths()
    
    return {
        'allure_dir': report_paths['allure'],
        'html_dir': report_paths['html'],
        'screenshots_dir': report_paths['screenshots'],
        'videos_dir': report_paths['videos'],
        'traces_dir': report_paths['traces'],
        'logs_dir': report_paths['logs'],
        'screenshot_on_failure': settings.screenshot_on_failure,
        'video_recording': settings.video_recording,
        'trace_recording': settings.trace_recording
    }


@pytest.fixture(scope="function")
def test_report_data(request):
    """
    Test report data fixture.
    
    Args:
        request: Pytest request object
        
    Returns:
        Dictionary for collecting test report data
    """
    test_data = {
        'test_name': request.node.name,
        'test_file': str(request.fspath),
        'start_time': datetime.now(),
        'end_time': None,
        'duration': None,
        'status': 'running',
        'screenshots': [],
        'error_message': None,
        'traceback': None,
        'attachments': [],
        'metadata': {}
    }
    
    yield test_data
    
    # Finalize test data
    test_data['end_time'] = datetime.now()
    test_data['duration'] = (test_data['end_time'] - test_data['start_time']).total_seconds()
    
    # Save test report data
    try:
        settings = get_settings()
        report_dir = Path(settings.html_report_dir)
        report_dir.mkdir(parents=True, exist_ok=True)
        
        test_report_file = report_dir / f"test_report_{test_data['test_name'].replace('/', '_')}.json"
        with open(test_report_file, 'w') as f:
            json.dump(test_data, f, indent=2, default=str)
        
    except Exception as e:
        log.error(f"Failed to save test report data: {e}")


@pytest.fixture(scope="function")
def screenshot_on_failure(request, page, test_report_data, report_config):
    """
    Automatic screenshot on failure fixture.
    
    Args:
        request: Pytest request object
        page: Page instance
        test_report_data: Test report data
        report_config: Report configuration
    """
    yield
    
    # Take screenshot if test failed and screenshot on failure is enabled
    if request.node.rep_call.failed and report_config['screenshot_on_failure']:
        try:
            screenshot_manager = ScreenshotManager(page)
            
            # Generate filename with test name and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_test_name = request.node.name.replace('/', '_').replace(':', '_')
            filename = f"{timestamp}_{clean_test_name}_failure"
            
            # Take failure screenshot
            screenshot_path = screenshot_manager.take_failure_screenshot(
                test_name=request.node.name,
                error_message=str(request.node.rep_call.longrepr) if request.node.rep_call.longrepr else "Unknown error"
            )
            
            # Add to test report data
            test_report_data['screenshots'].append(screenshot_path)
            test_report_data['status'] = 'failed'
            test_report_data['error_message'] = str(request.node.rep_call.longrepr) if request.node.rep_call.longrepr else "Unknown error"
            
            log.info(f"Failure screenshot captured: {screenshot_path}")
            
        except Exception as e:
            log.error(f"Failed to capture failure screenshot: {e}")


@pytest.fixture(scope="function")
def video_recording(page, report_config):
    """
    Video recording fixture.
    
    Args:
        page: Page instance
        report_config: Report configuration
    """
    if not report_config['video_recording']:
        yield
        return
    
    video_path = None
    try:
        settings = get_settings()
        videos_dir = Path(report_config['videos_dir'])
        videos_dir.mkdir(parents=True, exist_ok=True)
        
        # Start video recording
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = videos_dir / f"test_{timestamp}.webm"
        
        # Note: Video recording requires additional setup in context
        # This is a placeholder for video recording logic
        log.info("Video recording started")
        
        yield
        
    except Exception as e:
        log.error(f"Video recording failed: {e}")
        yield
    finally:
        try:
            # Stop video recording
            if video_path:
                log.info(f"Video recording saved: {video_path}")
        except Exception as e:
            log.error(f"Failed to save video recording: {e}")


@pytest.fixture(scope="function")
def trace_recording(page, report_config):
    """
    Trace recording fixture.
    
    Args:
        page: Page instance
        report_config: Report configuration
    """
    if not report_config['trace_recording']:
        yield
        return
    
    trace_path = None
    try:
        settings = get_settings()
        traces_dir = Path(report_config['traces_dir'])
        traces_dir.mkdir(parents=True, exist_ok=True)
        
        # Start trace recording
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        trace_path = traces_dir / f"test_{timestamp}.zip"
        
        # Note: Trace recording requires additional setup in context
        # This is a placeholder for trace recording logic
        log.info("Trace recording started")
        
        yield
        
    except Exception as e:
        log.error(f"Trace recording failed: {e}")
        yield
    finally:
        try:
            # Stop trace recording
            if trace_path:
                log.info(f"Trace recording saved: {trace_path}")
        except Exception as e:
            log.error(f"Failed to save trace recording: {e}")


@pytest.fixture(scope="session")
def allure_environment():
    """
    Allure environment properties fixture.
    
    Returns:
        Dictionary with environment properties
    """
    settings = get_settings()
    
    environment_properties = {
        'Environment': settings.test_env.value,
        'Base URL': settings.base_url,
        'Browser': settings.browser.value,
        'Headless': str(settings.headless),
        'Window Size': f"{settings.window_width}x{settings.window_height}",
        'Timeout': str(settings.explicit_wait),
        'Test Execution Time': datetime.now().isoformat(),
        'Python Version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        'Platform': os.name,
        'User Agent': 'Playwright Test'
    }
    
    # Write allure environment properties
    try:
        allure_dir = Path(settings.allure_report_dir)
        allure_dir.mkdir(parents=True, exist_ok=True)
        
        env_file = allure_dir / "environment.properties"
        with open(env_file, 'w') as f:
            for key, value in environment_properties.items():
                f.write(f"{key}={value}\n")
        
        log.info("Allure environment properties created")
        
    except Exception as e:
        log.error(f"Failed to create allure environment properties: {e}")
    
    return environment_properties


@pytest.fixture(scope="session")
def html_report_generator():
    """
    HTML report generator fixture.
    
    Returns:
        HTMLReportGenerator instance
    """
    class HTMLReportGenerator:
        def __init__(self):
            self.settings = get_settings()
            self.report_dir = Path(self.settings.html_report_dir)
            self.report_dir.mkdir(parents=True, exist_ok=True)
            self.test_results = []
        
        def add_test_result(self, test_data: Dict[str, Any]):
            """Add test result to report."""
            self.test_results.append(test_data)
        
        def generate_summary_report(self) -> str:
            """Generate HTML summary report."""
            total_tests = len(self.test_results)
            passed_tests = len([t for t in self.test_results if t['status'] == 'passed'])
            failed_tests = len([t for t in self.test_results if t['status'] == 'failed'])
            skipped_tests = len([t for t in self.test_results if t['status'] == 'skipped'])
            
            pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>ParaBank Test Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
                    .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
                    .metric {{ background: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; }}
                    .metric.passed {{ background: #d4edda; }}
                    .metric.failed {{ background: #f8d7da; }}
                    .metric.skipped {{ background: #fff3cd; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background: #f2f2f2; }}
                    .status.passed {{ color: green; }}
                    .status.failed {{ color: red; }}
                    .status.skipped {{ color: orange; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>ParaBank Test Execution Report</h1>
                    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="summary">
                    <div class="metric">
                        <h3>{total_tests}</h3>
                        <p>Total Tests</p>
                    </div>
                    <div class="metric passed">
                        <h3>{passed_tests}</h3>
                        <p>Passed ({pass_rate:.1f}%)</p>
                    </div>
                    <div class="metric failed">
                        <h3>{failed_tests}</h3>
                        <p>Failed</p>
                    </div>
                    <div class="metric skipped">
                        <h3>{skipped_tests}</h3>
                        <p>Skipped</p>
                    </div>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Test Name</th>
                            <th>Status</th>
                            <th>Duration (s)</th>
                            <th>Error Message</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for test in self.test_results:
                status_class = test['status']
                duration = test.get('duration', 0)
                error_msg = test.get('error_message', '')
                
                html_content += f"""
                        <tr>
                            <td>{test['test_name']}</td>
                            <td class="status {status_class}">{test['status'].upper()}</td>
                            <td>{duration:.2f}</td>
                            <td>{error_msg[:100]}{'...' if len(error_msg) > 100 else ''}</td>
                        </tr>
                """
            
            html_content += """
                    </tbody>
                </table>
            </body>
            </html>
            """
            
            return html_content
        
        def save_report(self, filename: str = "test_report.html"):
            """Save HTML report to file."""
            try:
                html_content = self.generate_summary_report()
                report_file = self.report_dir / filename
                
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                log.info(f"HTML report saved: {report_file}")
                return str(report_file)
                
            except Exception as e:
                log.error(f"Failed to save HTML report: {e}")
                return None
    
    return HTMLReportGenerator()


@pytest.fixture(scope="function", autouse=True)
def test_metadata_collector(request, test_report_data):
    """
    Automatic test metadata collector.
    
    Args:
        request: Pytest request object
        test_report_data: Test report data
    """
    # Collect test metadata
    test_report_data['metadata'] = {
        'markers': [marker.name for marker in request.node.iter_markers()],
        'node_id': request.node.nodeid,
        'function_name': request.node.name,
        'module_name': request.node.module.__name__,
        'cls_name': request.node.cls.__name__ if request.node.cls else None,
        'file_path': str(request.fspath),
        'line_number': request.node.lineno if hasattr(request.node, 'lineno') else None
    }


@pytest.fixture(scope="session")
def performance_metrics():
    """
    Performance metrics collector fixture.
    
    Returns:
        PerformanceMetricsCollector instance
    """
    class PerformanceMetricsCollector:
        def __init__(self):
            self.metrics = {}
            self.start_times = {}
        
        def start_timer(self, name: str):
            """Start performance timer."""
            self.start_times[name] = datetime.now()
        
        def end_timer(self, name: str) -> float:
            """End performance timer and return duration."""
            if name in self.start_times:
                duration = (datetime.now() - self.start_times[name]).total_seconds()
                if name not in self.metrics:
                    self.metrics[name] = []
                self.metrics[name].append(duration)
                return duration
            return 0.0
        
        def get_average(self, name: str) -> float:
            """Get average duration for metric."""
            if name in self.metrics and self.metrics[name]:
                return sum(self.metrics[name]) / len(self.metrics[name])
            return 0.0
        
        def get_max(self, name: str) -> float:
            """Get maximum duration for metric."""
            if name in self.metrics and self.metrics[name]:
                return max(self.metrics[name])
            return 0.0
        
        def get_min(self, name: str) -> float:
            """Get minimum duration for metric."""
            if name in self.metrics and self.metrics[name]:
                return min(self.metrics[name])
            return 0.0
        
        def get_all_metrics(self) -> Dict[str, Dict[str, float]]:
            """Get all calculated metrics."""
            results = {}
            for name in self.metrics:
                if self.metrics[name]:
                    results[name] = {
                        'count': len(self.metrics[name]),
                        'average': self.get_average(name),
                        'min': self.get_min(name),
                        'max': self.get_max(name),
                        'total': sum(self.metrics[name])
                    }
            return results
    
    return PerformanceMetricsCollector()
