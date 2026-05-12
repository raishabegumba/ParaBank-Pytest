"""Advanced HTML reporting for enterprise test framework."""
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from jinja2 import Template
from src.config.settings import get_settings
from src.config.logger import log


class HTMLReporter:
    """Enterprise-grade HTML reporting system."""
    
    def __init__(self):
        """Initialize HTML reporter."""
        self.settings = get_settings()
        self.report_dir = Path(self.settings.html_report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.test_results = []
        self.suite_results = {}
        self.execution_summary = {}
        
    def add_test_result(self, test_result: Dict[str, Any]):
        """Add test result to report.
        
        Args:
            test_result: Test result dictionary
        """
        try:
            # Add timestamp if not present
            if 'timestamp' not in test_result:
                test_result['timestamp'] = datetime.now().isoformat()
            
            self.test_results.append(test_result)
            
            # Update suite results
            suite_name = test_result.get('suite', 'Default')
            if suite_name not in self.suite_results:
                self.suite_results[suite_name] = {
                    'passed': 0,
                    'failed': 0,
                    'skipped': 0,
                    'total': 0,
                    'duration': 0.0
                }
            
            status = test_result.get('status', 'unknown')
            self.suite_results[suite_name]['total'] += 1
            self.suite_results[suite_name]['duration'] += test_result.get('duration', 0.0)
            
            if status == 'passed':
                self.suite_results[suite_name]['passed'] += 1
            elif status == 'failed':
                self.suite_results[suite_name]['failed'] += 1
            elif status == 'skipped':
                self.suite_results[suite_name]['skipped'] += 1
            
            log.info(f"Added test result: {test_result.get('test_name', 'unknown')} - {status}")
            
        except Exception as e:
            log.error(f"Failed to add test result: {e}")
    
    def calculate_execution_summary(self) -> Dict[str, Any]:
        """Calculate execution summary statistics.
        
        Returns:
            Execution summary dictionary
        """
        try:
            total_tests = len(self.test_results)
            passed_tests = len([t for t in self.test_results if t.get('status') == 'passed'])
            failed_tests = len([t for t in self.test_results if t.get('status') == 'failed'])
            skipped_tests = len([t for t in self.test_results if t.get('status') == 'skipped'])
            
            total_duration = sum(t.get('duration', 0.0) for t in self.test_results)
            pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0.0
            
            self.execution_summary = {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'skipped': skipped_tests,
                'pass_rate': pass_rate,
                'total_duration': total_duration,
                'average_duration': total_duration / total_tests if total_tests > 0 else 0.0,
                'execution_time': datetime.now().isoformat(),
                'environment': self.settings.test_env.value,
                'browser': self.settings.browser.value
            }
            
            return self.execution_summary
            
        except Exception as e:
            log.error(f"Failed to calculate execution summary: {e}")
            return {}
    
    def generate_dashboard_html(self) -> str:
        """Generate HTML dashboard report.
        
        Returns:
            HTML dashboard content
        """
        try:
            summary = self.calculate_execution_summary()
            
            html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ParaBank Test Report Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
        }
        
        .metric-card.passed {
            border-left: 5px solid #28a745;
        }
        
        .metric-card.failed {
            border-left: 5px solid #dc3545;
        }
        
        .metric-card.skipped {
            border-left: 5px solid #ffc107;
        }
        
        .metric-card.total {
            border-left: 5px solid #007bff;
        }
        
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .metric-label {
            font-size: 1.1em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .charts-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .chart-container {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .chart-container h3 {
            margin-bottom: 20px;
            color: #333;
        }
        
        .test-results-table {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .table-header {
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #dee2e6;
        }
        
        .table-header h3 {
            color: #333;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .status-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .status-badge.passed {
            background: #d4edda;
            color: #155724;
        }
        
        .status-badge.failed {
            background: #f8d7da;
            color: #721c24;
        }
        
        .status-badge.skipped {
            background: #fff3cd;
            color: #856404;
        }
        
        .duration {
            font-family: 'Courier New', monospace;
            color: #666;
        }
        
        .suite-summary {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .suite-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .suite-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }
        
        .suite-name {
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }
        
        .suite-stats {
            display: flex;
            gap: 15px;
            font-size: 0.9em;
        }
        
        .suite-stat {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .footer {
            text-align: center;
            padding: 30px;
            color: #666;
            margin-top: 50px;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .metrics-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }
            
            .charts-section {
                grid-template-columns: 1fr;
            }
            
            table {
                font-size: 0.9em;
            }
            
            th, td {
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 ParaBank Test Report Dashboard</h1>
            <p>Generated on {{ execution_time }} | Environment: {{ environment }} | Browser: {{ browser }}</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card total">
                <div class="metric-value">{{ total_tests }}</div>
                <div class="metric-label">Total Tests</div>
            </div>
            <div class="metric-card passed">
                <div class="metric-value">{{ passed }}</div>
                <div class="metric-label">Passed</div>
            </div>
            <div class="metric-card failed">
                <div class="metric-value">{{ failed }}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric-card skipped">
                <div class="metric-value">{{ skipped }}</div>
                <div class="metric-label">Skipped</div>
            </div>
        </div>
        
        <div class="charts-section">
            <div class="chart-container">
                <h3>Test Results Distribution</h3>
                <canvas id="resultsChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>Pass Rate</h3>
                <canvas id="passRateChart"></canvas>
            </div>
        </div>
        
        {% if suite_results %}
        <div class="suite-summary">
            <h3>Suite Summary</h3>
            <div class="suite-grid">
                {% for suite_name, suite_data in suite_results.items() %}
                <div class="suite-card">
                    <div class="suite-name">{{ suite_name }}</div>
                    <div class="suite-stats">
                        <div class="suite-stat">
                            <span style="color: #28a745;">✓ {{ suite_data.passed }}</span>
                        </div>
                        <div class="suite-stat">
                            <span style="color: #dc3545;">✗ {{ suite_data.failed }}</span>
                        </div>
                        <div class="suite-stat">
                            <span style="color: #ffc107;">⊘ {{ suite_data.skipped }}</span>
                        </div>
                        <div class="suite-stat">
                            <span>⏱ {{ "%.2f"|format(suite_data.duration) }}s</span>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        <div class="test-results-table">
            <div class="table-header">
                <h3>Test Results Details</h3>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Test Name</th>
                        <th>Suite</th>
                        <th>Status</th>
                        <th>Duration</th>
                        <th>Error Message</th>
                    </tr>
                </thead>
                <tbody>
                    {% for test in test_results %}
                    <tr>
                        <td>{{ test.test_name }}</td>
                        <td>{{ test.suite or 'N/A' }}</td>
                        <td>
                            <span class="status-badge {{ test.status }}">{{ test.status }}</span>
                        </td>
                        <td class="duration">{{ "%.3f"|format(test.duration or 0) }}s</td>
                        <td>{{ test.error_message[:100] if test.error_message else '' }}{{ '...' if test.error_message and test.error_message|length > 100 else '' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Generated by ParaBank Enterprise Test Framework | {{ execution_time }}</p>
        </div>
    </div>
    
    <script>
        // Test Results Chart
        const resultsCtx = document.getElementById('resultsChart').getContext('2d');
        new Chart(resultsCtx, {
            type: 'doughnut',
            data: {
                labels: ['Passed', 'Failed', 'Skipped'],
                datasets: [{
                    data: [{{ passed }}, {{ failed }}, {{ skipped }}],
                    backgroundColor: ['#28a745', '#dc3545', '#ffc107'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
        
        // Pass Rate Chart
        const passRateCtx = document.getElementById('passRateChart').getContext('2d');
        new Chart(passRateCtx, {
            type: 'gauge',
            data: {
                datasets: [{
                    data: [{{ pass_rate }}],
                    backgroundColor: [
                        '{{ "#dc3545" if pass_rate < 50 else "#ffc107" if pass_rate < 80 else "#28a745" }}'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return 'Pass Rate: {{ "%.1f"|format(pass_rate) }}%';
                            }
                        }
                    }
                }
            }
        });
    </script>
</body>
</html>
            """
            
            template = Template(html_template)
            html_content = template.render(
                **summary,
                test_results=self.test_results,
                suite_results=self.suite_results,
                execution_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            return html_content
            
        except Exception as e:
            log.error(f"Failed to generate HTML dashboard: {e}")
            return self._generate_fallback_html()
    
    def _generate_fallback_html(self) -> str:
        """Generate fallback HTML in case of template errors.
        
        Returns:
            Basic HTML content
        """
        try:
            summary = self.calculate_execution_summary()
            
            return f"""
<!DOCTYPE html>
<html>
<head>
    <title>ParaBank Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .metrics {{ display: flex; gap: 20px; margin: 20px 0; }}
        .metric {{ background: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f2f2f2; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .skipped {{ color: orange; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ParaBank Test Report</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="metrics">
        <div class="metric">
            <h3>{summary.get('total_tests', 0)}</h3>
            <p>Total Tests</p>
        </div>
        <div class="metric">
            <h3 class="passed">{summary.get('passed', 0)}</h3>
            <p>Passed</p>
        </div>
        <div class="metric">
            <h3 class="failed">{summary.get('failed', 0)}</h3>
            <p>Failed</p>
        </div>
        <div class="metric">
            <h3 class="skipped">{summary.get('skipped', 0)}</h3>
            <p>Skipped</p>
        </div>
    </div>
    
    <table>
        <thead>
            <tr>
                <th>Test Name</th>
                <th>Status</th>
                <th>Duration</th>
                <th>Error</th>
            </tr>
        </thead>
        <tbody>
            {"".join([
                f'<tr><td>{test.get("test_name", "Unknown")}</td>'
                f'<td class="{test.get("status", "unknown")}">{test.get("status", "unknown")}</td>'
                f'<td>{test.get("duration", 0):.3f}s</td>'
                f'<td>{(test.get("error_message", "") or "")[:100]}</td></tr>'
                for test in self.test_results
            ])}
        </tbody>
    </table>
</body>
</html>
            """
            
        except Exception as e:
            log.error(f"Failed to generate fallback HTML: {e}")
            return "<html><body><h1>Error generating report</h1></body></html>"
    
    def generate_detailed_test_report(self, test_name: str, test_data: Dict[str, Any]) -> str:
        """Generate detailed HTML report for a single test.
        
        Args:
            test_name: Test name
            test_data: Test data dictionary
            
        Returns:
            Detailed HTML report content
        """
        try:
            html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - {{ test_name }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
        }
        
        .header h1 {
            margin: 0;
            font-size: 2em;
        }
        
        .status-banner {
            padding: 20px;
            text-align: center;
            font-size: 1.2em;
            font-weight: bold;
        }
        
        .status-banner.passed {
            background: #d4edda;
            color: #155724;
        }
        
        .status-banner.failed {
            background: #f8d7da;
            color: #721c24;
        }
        
        .status-banner.skipped {
            background: #fff3cd;
            color: #856404;
        }
        
        .section {
            padding: 25px;
            border-bottom: 1px solid #eee;
        }
        
        .section h3 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.3em;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        
        .info-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
        }
        
        .info-label {
            font-weight: 600;
            color: #666;
            margin-bottom: 5px;
        }
        
        .info-value {
            color: #333;
        }
        
        .error-details {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 5px;
            padding: 20px;
            margin-top: 15px;
        }
        
        .error-details h4 {
            color: #721c24;
            margin-bottom: 10px;
        }
        
        .error-message {
            font-family: 'Courier New', monospace;
            background: #fff;
            padding: 15px;
            border-radius: 3px;
            white-space: pre-wrap;
            word-break: break-all;
        }
        
        .attachments {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 15px;
        }
        
        .attachment {
            background: #e9ecef;
            padding: 10px 15px;
            border-radius: 5px;
            text-decoration: none;
            color: #495057;
            transition: background 0.3s ease;
        }
        
        .attachment:hover {
            background: #dee2e6;
        }
        
        .screenshot {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-top: 15px;
        }
        
        .timeline {
            position: relative;
            padding-left: 30px;
        }
        
        .timeline::before {
            content: '';
            position: absolute;
            left: 10px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: #dee2e6;
        }
        
        .timeline-item {
            position: relative;
            margin-bottom: 20px;
        }
        
        .timeline-item::before {
            content: '';
            position: absolute;
            left: -25px;
            top: 5px;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #007bff;
        }
        
        .timeline-time {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }
        
        .timeline-content {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Test Report: {{ test_name }}</h1>
            <p>Generated on {{ execution_time }}</p>
        </div>
        
        <div class="status-banner {{ status }}">
            Status: {{ status.upper() }}
        </div>
        
        <div class="section">
            <h3>Test Information</h3>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Test Suite</div>
                    <div class="info-value">{{ suite or 'N/A' }}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Duration</div>
                    <div class="info-value">{{ "%.3f"|format(duration or 0) }} seconds</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Environment</div>
                    <div class="info-value">{{ environment }}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Browser</div>
                    <div class="info-value">{{ browser }}</div>
                </div>
            </div>
        </div>
        
        {% if metadata %}
        <div class="section">
            <h3>Test Metadata</h3>
            <div class="info-grid">
                {% for key, value in metadata.items() %}
                <div class="info-item">
                    <div class="info-label">{{ key.replace('_', ' ').title() }}</div>
                    <div class="info-value">{{ value }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        {% if error_message %}
        <div class="section">
            <h3>Error Details</h3>
            <div class="error-details">
                <h4>❌ Error Message</h4>
                <div class="error-message">{{ error_message }}</div>
            </div>
        </div>
        {% endif %}
        
        {% if attachments %}
        <div class="section">
            <h3>Attachments</h3>
            <div class="attachments">
                {% for attachment in attachments %}
                {% if attachment.type == 'screenshot' %}
                <div>
                    <h4>{{ attachment.name }}</h4>
                    {% if attachment.path %}
                    <img src="{{ attachment.path }}" alt="{{ attachment.name }}" class="screenshot">
                    {% endif %}
                </div>
                {% else %}
                <a href="#" class="attachment">{{ attachment.name }}</a>
                {% endif %}
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        {% if performance_metrics %}
        <div class="section">
            <h3>Performance Metrics</h3>
            <div class="info-grid">
                {% for metric_name, value in performance_metrics.items() %}
                <div class="info-item">
                    <div class="info-label">{{ metric_name.replace('_', ' ').title() }}</div>
                    <div class="info-value">{{ "%.3f"|format(value) }} seconds</div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        <div class="section">
            <h3>Execution Timeline</h3>
            <div class="timeline">
                <div class="timeline-item">
                    <div class="timeline-time">{{ start_time }}</div>
                    <div class="timeline-content">Test Started</div>
                </div>
                {% if end_time %}
                <div class="timeline-item">
                    <div class="timeline-time">{{ end_time }}</div>
                    <div class="timeline-content">Test {{ status.title() }}</div>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
            """
            
            template = Template(html_template)
            html_content = template.render(
                test_name=test_name,
                execution_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                **test_data
            )
            
            return html_content
            
        except Exception as e:
            log.error(f"Failed to generate detailed test report: {e}")
            return f"<html><body><h1>Error generating report for {test_name}</h1></body></html>"
    
    def save_dashboard_report(self, filename: str = "dashboard.html") -> str:
        """Save dashboard HTML report.
        
        Args:
            filename: Report filename
            
        Returns:
            Path to saved report
        """
        try:
            html_content = self.generate_dashboard_html()
            report_path = self.report_dir / filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            log.info(f"Dashboard report saved: {report_path}")
            return str(report_path)
            
        except Exception as e:
            log.error(f"Failed to save dashboard report: {e}")
            return ""
    
    def save_test_report(self, test_name: str, test_data: Dict[str, Any]) -> str:
        """Save detailed test report.
        
        Args:
            test_name: Test name
            test_data: Test data
            
        Returns:
            Path to saved report
        """
        try:
            html_content = self.generate_detailed_test_report(test_name, test_data)
            safe_filename = test_name.replace('/', '_').replace(':', '_') + ".html"
            report_path = self.report_dir / "tests" / safe_filename
            
            # Ensure tests directory exists
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            log.info(f"Test report saved: {report_path}")
            return str(report_path)
            
        except Exception as e:
            log.error(f"Failed to save test report: {e}")
            return ""
    
    def save_json_report(self, filename: str = "test_results.json") -> str:
        """Save test results as JSON.
        
        Args:
            filename: JSON filename
            
        Returns:
            Path to saved JSON
        """
        try:
            report_data = {
                'execution_summary': self.calculate_execution_summary(),
                'suite_results': self.suite_results,
                'test_results': self.test_results,
                'generated_at': datetime.now().isoformat()
            }
            
            json_path = self.report_dir / filename
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            log.info(f"JSON report saved: {json_path}")
            return str(json_path)
            
        except Exception as e:
            log.error(f"Failed to save JSON report: {e}")
            return ""
    
    def generate_all_reports(self) -> Dict[str, str]:
        """Generate all report types.
        
        Returns:
            Dictionary of report paths
        """
        try:
            reports = {
                'dashboard': self.save_dashboard_report(),
                'json': self.save_json_report()
            }
            
            # Generate individual test reports
            for test_result in self.test_results:
                test_name = test_result.get('test_name', 'unknown_test')
                test_report_path = self.save_test_report(test_name, test_result)
                reports[f'test_{test_name}'] = test_report_path
            
            log.info(f"Generated {len(reports)} reports")
            return reports
            
        except Exception as e:
            log.error(f"Failed to generate all reports: {e}")
            return {}


# Global HTML reporter instance
_html_reporter = None


def get_html_reporter() -> HTMLReporter:
    """Get global HTML reporter instance.
    
    Returns:
        HTMLReporter instance
    """
    global _html_reporter
    
    if _html_reporter is None:
        _html_reporter = HTMLReporter()
    
    return _html_reporter


def add_test_result_to_report(test_result: Dict[str, Any]):
    """Add test result to global HTML reporter.
    
    Args:
        test_result: Test result dictionary
    """
    reporter = get_html_reporter()
    reporter.add_test_result(test_result)


def generate_html_reports() -> Dict[str, str]:
    """Generate all HTML reports using global reporter.
    
    Returns:
        Dictionary of report paths
    """
    reporter = get_html_reporter()
    return reporter.generate_all_reports()
