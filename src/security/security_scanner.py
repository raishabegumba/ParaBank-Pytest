"""Advanced security scanner for comprehensive security testing."""
import re
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
from playwright.sync_api import Page, Response
from src.config.settings import get_settings
from src.config.logger import log


class SecurityScanner:
    """Enterprise-grade security scanner for web applications."""
    
    def __init__(self, page: Page):
        """Initialize security scanner.
        
        Args:
            page: Playwright page instance
        """
        self.page = page
        self.settings = get_settings()
        self.base_url = self.settings.base_url
        self.vulnerabilities = []
        self.scan_results = {}
        
        # Security test payloads
        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
            "<iframe src=javascript:alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<input autofocus onfocus=alert('XSS')>",
            "<select onfocus=alert('XSS') autofocus>",
            "<textarea onfocus=alert('XSS') autofocus>",
            "<keygen onfocus=alert('XSS') autofocus>",
            "<video><source onerror=alert('XSS')>",
            "<audio><source onerror=alert('XSS')>",
            "<details open ontoggle=alert('XSS')>",
            "<marquee onstart=alert('XSS')>",
            "<video controls onplay=alert('XSS')>",
            "<video controls onpause=alert('XSS')>",
            "<audio controls onplay=alert('XSS')>",
            "<body onscroll=alert('XSS')>",
            "<img src=x onerror=alert(String.fromCharCode(88,83,83))>"
        ]
        
        self.sql_injection_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "'; DROP TABLE users;--",
            "' UNION SELECT * FROM users--",
            "admin'--",
            "admin'/*",
            "' OR 1=1#",
            "' OR 'a'='a",
            "1' OR '1'='1' --",
            "x'; DROP TABLE users; --",
            "' OR 'x'='x",
            "' OR 1=1--",
            "' OR 1=1#",
            "' OR 1=1/*",
            "') OR '1'='1--",
            "') OR ('1'='1--",
            "1' OR '1'='1'--",
            "1' OR '1'='1#",
            "1' OR '1'='1/*",
            "') OR ('1'='1--"
        ]
        
        self.path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\system.ini",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd%00",
            "..%252f..%252f..%252fetc%252fpasswd",
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
            "..%c1%9c..%c1%9c..%c1%9cetc%c1%9cpasswd"
        ]
        
        self.csrf_tokens = []
        
    def scan_xss_vulnerabilities(self, target_url: str) -> Dict[str, Any]:
        """Scan for XSS vulnerabilities.
        
        Args:
            target_url: URL to scan
            
        Returns:
            XSS scan results
        """
        log.info(f"Starting XSS vulnerability scan for: {target_url}")
        
        xss_results = {
            'vulnerabilities': [],
            'tested_payloads': len(self.xss_payloads),
            'vulnerable_endpoints': [],
            'scan_time': time.time()
        }
        
        try:
            # Navigate to target page
            self.page.goto(target_url)
            self.page.wait_for_load_state('networkidle')
            
            # Find all input fields and forms
            forms = self.page.locator('form')
            input_fields = self.page.locator('input, textarea, select')
            
            for i in range(forms.count()):
                form = forms.nth(i)
                
                # Get form action and method
                action = form.get_attribute('action') or ''
                method = form.get_attribute('method') or 'GET'
                
                # Find input fields in this form
                form_inputs = form.locator('input, textarea')
                
                for j in range(form_inputs.count()):
                    input_field = form_inputs.nth(j)
                    input_type = input_field.get_attribute('type') or 'text'
                    input_name = input_field.get_attribute('name') or f'input_{j}'
                    
                    # Skip password fields for XSS testing
                    if input_type == 'password':
                        continue
                    
                    # Test XSS payloads
                    for payload in self.xss_payloads:
                        try:
                            # Fill the input field with XSS payload
                            input_field.fill(payload)
                            
                            # Submit the form or trigger event
                            if method.lower() == 'post':
                                form.locator('input[type="submit"], button[type="submit"]').click()
                            else:
                                input_field.press('Enter')
                            
                            # Wait for response
                            self.page.wait_for_load_state('networkidle')
                            
                            # Check if XSS payload executed
                            page_content = self.page.content()
                            
                            if self._check_xss_execution(page_content, payload):
                                vulnerability = {
                                    'type': 'XSS',
                                    'severity': 'High',
                                    'endpoint': action or target_url,
                                    'payload': payload,
                                    'input_field': input_name,
                                    'method': method,
                                    'description': f'XSS vulnerability found in {input_name} field'
                                }
                                
                                xss_results['vulnerabilities'].append(vulnerability)
                                xss_results['vulnerable_endpoints'].append(action or target_url)
                                
                                log.warning(f"XSS vulnerability detected: {vulnerability}")
                            
                            # Go back to original page
                            self.page.goto(target_url)
                            self.page.wait_for_load_state('networkidle')
                            
                        except Exception as e:
                            log.debug(f"Error testing XSS payload {payload}: {e}")
                            continue
            
            # Test URL-based XSS
            self._test_url_based_xss(target_url, xss_results)
            
        except Exception as e:
            log.error(f"XSS scan failed: {e}")
            xss_results['error'] = str(e)
        
        xss_results['vulnerability_count'] = len(xss_results['vulnerabilities'])
        xss_results['scan_duration'] = time.time() - xss_results['scan_time']
        
        log.info(f"XSS scan completed: {xss_results['vulnerability_count']} vulnerabilities found")
        return xss_results
    
    def _test_url_based_xss(self, target_url: str, results: Dict[str, Any]):
        """Test URL-based XSS vulnerabilities.
        
        Args:
            target_url: Target URL
            results: Results dictionary to update
        """
        try:
            parsed_url = urlparse(target_url)
            base_params = dict(param.split('=') for param in parsed_url.query.split('&') if '=' in param)
            
            for payload in self.xss_payloads[:5]:  # Test limited payloads for URL
                test_params = base_params.copy()
                
                # Test each parameter with XSS payload
                for param_name in test_params:
                    test_params[param_name] = payload
                    
                    # Construct test URL
                    test_query = '&'.join(f"{k}={v}" for k, v in test_params.items())
                    test_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{test_query}"
                    
                    try:
                        self.page.goto(test_url)
                        self.page.wait_for_load_state('networkidle')
                        
                        page_content = self.page.content()
                        
                        if self._check_xss_execution(page_content, payload):
                            vulnerability = {
                                'type': 'URL-based XSS',
                                'severity': 'High',
                                'endpoint': test_url,
                                'payload': payload,
                                'parameter': param_name,
                                'method': 'GET',
                                'description': f'URL-based XSS in parameter {param_name}'
                            }
                            
                            results['vulnerabilities'].append(vulnerability)
                            results['vulnerable_endpoints'].append(test_url)
                            
                            log.warning(f"URL-based XSS detected: {vulnerability}")
                        
                    except Exception as e:
                        log.debug(f"Error testing URL XSS: {e}")
                        continue
                        
        except Exception as e:
            log.error(f"URL-based XSS test failed: {e}")
    
    def _check_xss_execution(self, page_content: str, payload: str) -> bool:
        """Check if XSS payload was executed.
        
        Args:
            page_content: Page HTML content
            payload: XSS payload that was tested
            
        Returns:
            True if XSS was executed
        """
        # Check for script tags in response
        if '<script>' in page_content.lower() and 'alert' in page_content.lower():
            return True
        
        # Check for JavaScript execution indicators
        js_indicators = [
            'javascript:',
            'onerror=',
            'onload=',
            'onclick=',
            'onfocus=',
            'onmouseover='
        ]
        
        for indicator in js_indicators:
            if indicator in page_content.lower():
                return True
        
        # Check for reflected payload
        if payload.replace('<', '&lt;').replace('>', '&gt;') in page_content:
            return True
        
        return False
    
    def scan_sql_injection_vulnerabilities(self, target_url: str) -> Dict[str, Any]:
        """Scan for SQL injection vulnerabilities.
        
        Args:
            target_url: URL to scan
            
        Returns:
            SQL injection scan results
        """
        log.info(f"Starting SQL injection scan for: {target_url}")
        
        sql_results = {
            'vulnerabilities': [],
            'tested_payloads': len(self.sql_injection_payloads),
            'vulnerable_endpoints': [],
            'scan_time': time.time()
        }
        
        try:
            # Navigate to target page
            self.page.goto(target_url)
            self.page.wait_for_load_state('networkidle')
            
            # Find forms and input fields
            forms = self.page.locator('form')
            
            for i in range(forms.count()):
                form = forms.nth(i)
                action = form.get_attribute('action') or ''
                method = form.get_attribute('method') or 'GET'
                
                # Find input fields
                input_fields = form.locator('input[type="text"], input[type="search"], textarea')
                
                for j in range(input_fields.count()):
                    input_field = input_fields.nth(j)
                    input_name = input_field.get_attribute('name') or f'input_{j}'
                    
                    # Test SQL injection payloads
                    for payload in self.sql_injection_payloads:
                        try:
                            # Fill input with SQL payload
                            input_field.fill(payload)
                            
                            # Submit form
                            if method.lower() == 'post':
                                form.locator('input[type="submit"], button[type="submit"]').click()
                            else:
                                input_field.press('Enter')
                            
                            # Wait for response
                            self.page.wait_for_load_state('networkidle')
                            
                            # Check for SQL error indicators
                            page_content = self.page.content()
                            
                            if self._check_sql_error(page_content):
                                vulnerability = {
                                    'type': 'SQL Injection',
                                    'severity': 'Critical',
                                    'endpoint': action or target_url,
                                    'payload': payload,
                                    'input_field': input_name,
                                    'method': method,
                                    'description': f'SQL injection vulnerability in {input_name} field'
                                }
                                
                                sql_results['vulnerabilities'].append(vulnerability)
                                sql_results['vulnerable_endpoints'].append(action or target_url)
                                
                                log.warning(f"SQL injection detected: {vulnerability}")
                            
                            # Go back to original page
                            self.page.goto(target_url)
                            self.page.wait_for_load_state('networkidle')
                            
                        except Exception as e:
                            log.debug(f"Error testing SQL payload {payload}: {e}")
                            continue
            
            # Test URL-based SQL injection
            self._test_url_based_sql_injection(target_url, sql_results)
            
        except Exception as e:
            log.error(f"SQL injection scan failed: {e}")
            sql_results['error'] = str(e)
        
        sql_results['vulnerability_count'] = len(sql_results['vulnerabilities'])
        sql_results['scan_duration'] = time.time() - sql_results['scan_time']
        
        log.info(f"SQL injection scan completed: {sql_results['vulnerability_count']} vulnerabilities found")
        return sql_results
    
    def _test_url_based_sql_injection(self, target_url: str, results: Dict[str, Any]):
        """Test URL-based SQL injection vulnerabilities.
        
        Args:
            target_url: Target URL
            results: Results dictionary to update
        """
        try:
            parsed_url = urlparse(target_url)
            base_params = dict(param.split('=') for param in parsed_url.query.split('&') if '=' in param)
            
            for payload in self.sql_injection_payloads[:3]:  # Test limited payloads for URL
                test_params = base_params.copy()
                
                for param_name in test_params:
                    test_params[param_name] = payload
                    
                    test_query = '&'.join(f"{k}={v}" for k, v in test_params.items())
                    test_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{test_query}"
                    
                    try:
                        self.page.goto(test_url)
                        self.page.wait_for_load_state('networkidle')
                        
                        page_content = self.page.content()
                        
                        if self._check_sql_error(page_content):
                            vulnerability = {
                                'type': 'URL-based SQL Injection',
                                'severity': 'Critical',
                                'endpoint': test_url,
                                'payload': payload,
                                'parameter': param_name,
                                'method': 'GET',
                                'description': f'URL-based SQL injection in parameter {param_name}'
                            }
                            
                            results['vulnerabilities'].append(vulnerability)
                            results['vulnerable_endpoints'].append(test_url)
                            
                            log.warning(f"URL-based SQL injection detected: {vulnerability}")
                        
                    except Exception as e:
                        log.debug(f"Error testing URL SQL injection: {e}")
                        continue
                        
        except Exception as e:
            log.error(f"URL-based SQL injection test failed: {e}")
    
    def _check_sql_error(self, page_content: str) -> bool:
        """Check for SQL error indicators in page content.
        
        Args:
            page_content: Page HTML content
            
        Returns:
            True if SQL error detected
        """
        sql_error_patterns = [
            r"SQL syntax.*MySQL",
            r"Warning.*mysql_.*",
            r"valid MySQL result",
            r"MySqlClient\.",
            r"PostgreSQL query failed",
            r"Warning.*pg_.*",
            r"valid PostgreSQL result",
            r"Npgsql\.",
            r"Microsoft OLE DB Provider for ODBC Drivers error",
            r"ODBC Microsoft Access Driver",
            r"Microsoft JET Database Engine",
            r"ODBC Microsoft Access",
            r"Oracle error",
            r"Oracle driver",
            r"CLI Driver.*ORA-[0-9][0-9][0-9][0-9]",
            r"Warning.*oci_.*",
            r"Warning.*ora_.*"
        ]
        
        for pattern in sql_error_patterns:
            if re.search(pattern, page_content, re.IGNORECASE):
                return True
        
        # Check for common SQL error messages
        sql_error_messages = [
            "sql syntax",
            "mysql_fetch",
            "ora-",
            "microsoft odbc",
            "odbc drivers error",
            "warning: mysql",
            "valid mysql result",
            "postgresql query failed"
        ]
        
        page_content_lower = page_content.lower()
        for error_msg in sql_error_messages:
            if error_msg in page_content_lower:
                return True
        
        return False
    
    def scan_path_traversal_vulnerabilities(self, target_url: str) -> Dict[str, Any]:
        """Scan for path traversal vulnerabilities.
        
        Args:
            target_url: URL to scan
            
        Returns:
            Path traversal scan results
        """
        log.info(f"Starting path traversal scan for: {target_url}")
        
        traversal_results = {
            'vulnerabilities': [],
            'tested_payloads': len(self.path_traversal_payloads),
            'vulnerable_endpoints': [],
            'scan_time': time.time()
        }
        
        try:
            parsed_url = urlparse(target_url)
            base_params = dict(param.split('=') for param in parsed_url.query.split('&') if '=' in param)
            
            for payload in self.path_traversal_payloads:
                test_params = base_params.copy()
                
                # Test each parameter
                for param_name in test_params:
                    test_params[param_name] = payload
                    
                    test_query = '&'.join(f"{k}={v}" for k, v in test_params.items())
                    test_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{test_query}"
                    
                    try:
                        self.page.goto(test_url)
                        self.page.wait_for_load_state('networkidle')
                        
                        page_content = self.page.content()
                        
                        # Check for system file indicators
                        if self._check_path_traversal_success(page_content):
                            vulnerability = {
                                'type': 'Path Traversal',
                                'severity': 'High',
                                'endpoint': test_url,
                                'payload': payload,
                                'parameter': param_name,
                                'method': 'GET',
                                'description': f'Path traversal vulnerability in parameter {param_name}'
                            }
                            
                            traversal_results['vulnerabilities'].append(vulnerability)
                            traversal_results['vulnerable_endpoints'].append(test_url)
                            
                            log.warning(f"Path traversal detected: {vulnerability}")
                        
                    except Exception as e:
                        log.debug(f"Error testing path traversal: {e}")
                        continue
                        
        except Exception as e:
            log.error(f"Path traversal scan failed: {e}")
            traversal_results['error'] = str(e)
        
        traversal_results['vulnerability_count'] = len(traversal_results['vulnerabilities'])
        traversal_results['scan_duration'] = time.time() - traversal_results['scan_time']
        
        log.info(f"Path traversal scan completed: {traversal_results['vulnerability_count']} vulnerabilities found")
        return traversal_results
    
    def _check_path_traversal_success(self, page_content: str) -> bool:
        """Check if path traversal was successful.
        
        Args:
            page_content: Page HTML content
            
        Returns:
            True if path traversal successful
        """
        # Check for Linux system file indicators
        linux_indicators = [
            "root:x:0:0",
            "bin:x:1:1",
            "daemon:x:2:2",
            "sys:x:3:3",
            "[boot loader]",
            "operating systems"
        ]
        
        # Check for Windows system file indicators
        windows_indicators = [
            "[fonts]",
            "[extensions]",
            "[files]",
            "for 16-bit app support"
        ]
        
        page_content_lower = page_content.lower()
        
        for indicator in linux_indicators + windows_indicators:
            if indicator.lower() in page_content_lower:
                return True
        
        return False
    
    def scan_csrf_vulnerabilities(self, target_url: str) -> Dict[str, Any]:
        """Scan for CSRF vulnerabilities.
        
        Args:
            target_url: URL to scan
            
        Returns:
            CSRF scan results
        """
        log.info(f"Starting CSRF vulnerability scan for: {target_url}")
        
        csrf_results = {
            'vulnerabilities': [],
            'forms_analyzed': 0,
            'forms_with_tokens': 0,
            'vulnerable_forms': 0,
            'scan_time': time.time()
        }
        
        try:
            # Navigate to target page
            self.page.goto(target_url)
            self.page.wait_for_load_state('networkidle')
            
            # Find all forms
            forms = self.page.locator('form')
            csrf_results['forms_analyzed'] = forms.count()
            
            for i in range(forms.count()):
                form = forms.nth(i)
                action = form.get_attribute('action') or ''
                method = form.get_attribute('method') or 'GET'
                
                # Skip GET forms for CSRF (they are not vulnerable)
                if method.upper() == 'GET':
                    continue
                
                # Look for CSRF tokens
                has_csrf_token = False
                
                # Check for hidden inputs with CSRF-like names
                hidden_inputs = form.locator('input[type="hidden"]')
                for j in range(hidden_inputs.count()):
                    hidden_input = hidden_inputs.nth(j)
                    input_name = hidden_input.get_attribute('name') or ''
                    
                    csrf_token_names = [
                        'csrf_token', 'csrf', '_token', 'authenticity_token',
                        'synchronizer_token', 'xsrf_token', 'anti_csrf_token',
                        'request_token', 'nonce', 'state'
                    ]
                    
                    if any(token_name in input_name.lower() for token_name in csrf_token_names):
                        has_csrf_token = True
                        csrf_results['forms_with_tokens'] += 1
                        break
                
                # Check for CSRF token in meta tags
                if not has_csrf_token:
                    meta_tags = self.page.locator('meta[name*="csrf"], meta[name*="token"]')
                    if meta_tags.count() > 0:
                        has_csrf_token = True
                        csrf_results['forms_with_tokens'] += 1
                
                # If no CSRF token found, it's potentially vulnerable
                if not has_csrf_token:
                    vulnerability = {
                        'type': 'CSRF',
                        'severity': 'Medium',
                        'endpoint': action or target_url,
                        'method': method,
                        'description': f'Form without CSRF protection: {action or target_url}'
                    }
                    
                    csrf_results['vulnerabilities'].append(vulnerability)
                    csrf_results['vulnerable_forms'] += 1
                    
                    log.warning(f"CSRF vulnerability detected: {vulnerability}")
            
        except Exception as e:
            log.error(f"CSRF scan failed: {e}")
            csrf_results['error'] = str(e)
        
        csrf_results['vulnerability_count'] = len(csrf_results['vulnerabilities'])
        csrf_results['scan_duration'] = time.time() - csrf_results['scan_time']
        
        log.info(f"CSRF scan completed: {csrf_results['vulnerability_count']} vulnerabilities found")
        return csrf_results
    
    def scan_security_headers(self, target_url: str) -> Dict[str, Any]:
        """Scan for missing security headers.
        
        Args:
            target_url: URL to scan
            
        Returns:
            Security headers scan results
        """
        log.info(f"Starting security headers scan for: {target_url}")
        
        headers_results = {
            'missing_headers': [],
            'present_headers': [],
            'security_score': 0,
            'scan_time': time.time()
        }
        
        # Required security headers
        required_headers = {
            'X-Frame-Options': 'Prevents clickjacking',
            'X-XSS-Protection': 'Enables XSS protection',
            'X-Content-Type-Options': 'Prevents MIME sniffing',
            'Strict-Transport-Security': 'Enforces HTTPS',
            'Content-Security-Policy': 'Prevents XSS and data injection',
            'Referrer-Policy': 'Controls referrer information',
            'Permissions-Policy': 'Controls browser features'
        }
        
        try:
            # Navigate to target page and capture response headers
            response = None
            
            def capture_response(response_obj: Response):
                nonlocal response
                if response_obj.url == target_url:
                    response = response_obj
            
            self.page.route('**/*', lambda route: route.continue_())
            self.page.goto(target_url)
            self.page.wait_for_load_state('networkidle')
            
            if response:
                headers = response.headers
                headers_results['present_headers'] = list(headers.keys())
                
                # Check for missing security headers
                for header, description in required_headers.items():
                    if header not in headers:
                        vulnerability = {
                            'type': 'Missing Security Header',
                            'severity': 'Medium',
                            'header': header,
                            'description': f'Missing security header: {header} - {description}'
                        }
                        
                        headers_results['missing_headers'].append(vulnerability)
                    else:
                        headers_results['security_score'] += 1
                
                # Calculate security score
                headers_results['security_score'] = int(
                    (headers_results['security_score'] / len(required_headers)) * 100
                )
                
                log.info(f"Security headers scan completed: Score {headers_results['security_score']}%")
            
        except Exception as e:
            log.error(f"Security headers scan failed: {e}")
            headers_results['error'] = str(e)
        
        headers_results['vulnerability_count'] = len(headers_results['missing_headers'])
        headers_results['scan_duration'] = time.time() - headers_results['scan_time']
        
        return headers_results
    
    def run_comprehensive_security_scan(self, target_url: str) -> Dict[str, Any]:
        """Run comprehensive security scan.
        
        Args:
            target_url: Base URL to scan
            
        Returns:
            Comprehensive scan results
        """
        log.info(f"Starting comprehensive security scan for: {target_url}")
        
        scan_start_time = time.time()
        
        comprehensive_results = {
            'scan_summary': {
                'target_url': target_url,
                'scan_start_time': scan_start_time,
                'total_vulnerabilities': 0,
                'high_risk_vulnerabilities': 0,
                'medium_risk_vulnerabilities': 0,
                'low_risk_vulnerabilities': 0
            },
            'xss_scan': {},
            'sql_injection_scan': {},
            'path_traversal_scan': {},
            'csrf_scan': {},
            'security_headers_scan': {}
        }
        
        try:
            # Run individual scans
            comprehensive_results['xss_scan'] = self.scan_xss_vulnerabilities(target_url)
            comprehensive_results['sql_injection_scan'] = self.scan_sql_injection_vulnerabilities(target_url)
            comprehensive_results['path_traversal_scan'] = self.scan_path_traversal_vulnerabilities(target_url)
            comprehensive_results['csrf_scan'] = self.scan_csrf_vulnerabilities(target_url)
            comprehensive_results['security_headers_scan'] = self.scan_security_headers(target_url)
            
            # Aggregate results
            all_vulnerabilities = []
            
            for scan_type, scan_results in comprehensive_results.items():
                if scan_type != 'scan_summary' and 'vulnerabilities' in scan_results:
                    all_vulnerabilities.extend(scan_results['vulnerabilities'])
            
            # Categorize vulnerabilities
            for vuln in all_vulnerabilities:
                severity = vuln.get('severity', 'Low').lower()
                if severity in ['critical', 'high']:
                    comprehensive_results['scan_summary']['high_risk_vulnerabilities'] += 1
                elif severity == 'medium':
                    comprehensive_results['scan_summary']['medium_risk_vulnerabilities'] += 1
                else:
                    comprehensive_results['scan_summary']['low_risk_vulnerabilities'] += 1
            
            comprehensive_results['scan_summary']['total_vulnerabilities'] = len(all_vulnerabilities)
            comprehensive_results['scan_summary']['scan_duration'] = time.time() - scan_start_time
            comprehensive_results['scan_summary']['scan_end_time'] = time.time()
            
            # Calculate overall risk score
            risk_score = self._calculate_risk_score(comprehensive_results)
            comprehensive_results['scan_summary']['risk_score'] = risk_score
            
            log.info(f"Comprehensive security scan completed: {len(all_vulnerabilities)} vulnerabilities found")
            
        except Exception as e:
            log.error(f"Comprehensive security scan failed: {e}")
            comprehensive_results['error'] = str(e)
        
        return comprehensive_results
    
    def _calculate_risk_score(self, scan_results: Dict[str, Any]) -> int:
        """Calculate overall risk score.
        
        Args:
            scan_results: Comprehensive scan results
            
        Returns:
            Risk score (0-100)
        """
        summary = scan_results['scan_summary']
        
        # Weight vulnerabilities by severity
        critical_weight = 10
        high_weight = 7
        medium_weight = 4
        low_weight = 1
        
        risk_score = (
            summary['high_risk_vulnerabilities'] * critical_weight +
            summary['medium_risk_vulnerabilities'] * medium_weight +
            summary['low_risk_vulnerabilities'] * low_weight
        )
        
        # Normalize to 0-100 scale
        max_possible_score = 100
        normalized_score = min(risk_score, max_possible_score)
        
        return normalized_score
    
    def generate_security_report(self, scan_results: Dict[str, Any]) -> str:
        """Generate comprehensive security report.
        
        Args:
            scan_results: Scan results dictionary
            
        Returns:
            HTML report content
        """
        try:
            summary = scan_results.get('scan_summary', {})
            
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Scan Report - {summary.get('target_url', 'Unknown')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; margin-bottom: 10px; }}
        .risk-high {{ color: #dc3545; }}
        .risk-medium {{ color: #ffc107; }}
        .risk-low {{ color: #28a745; }}
        .vulnerability {{ background: #fff; border: 1px solid #ddd; padding: 20px; margin-bottom: 20px; border-radius: 8px; }}
        .vulnerability h3 {{ margin-top: 0; }}
        .severity-critical {{ border-left: 5px solid #dc3545; }}
        .severity-high {{ border-left: 5px solid #fd7e14; }}
        .severity-medium {{ border-left: 5px solid #ffc107; }}
        .severity-low {{ border-left: 5px solid #28a745; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #f8f9fa; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Security Scan Report</h1>
            <p>Target: {summary.get('target_url', 'Unknown')}</p>
            <p>Scan Date: {datetime.fromtimestamp(summary.get('scan_start_time', time.time())).strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Duration: {summary.get('scan_duration', 0):.2f} seconds</p>
        </div>
        
        <div class="summary">
            <div class="metric">
                <div class="metric-value risk-high">{summary.get('total_vulnerabilities', 0)}</div>
                <div>Total Vulnerabilities</div>
            </div>
            <div class="metric">
                <div class="metric-value risk-high">{summary.get('high_risk_vulnerabilities', 0)}</div>
                <div>High Risk</div>
            </div>
            <div class="metric">
                <div class="metric-value risk-medium">{summary.get('medium_risk_vulnerabilities', 0)}</div>
                <div>Medium Risk</div>
            </div>
            <div class="metric">
                <div class="metric-value risk-low">{summary.get('low_risk_vulnerabilities', 0)}</div>
                <div>Low Risk</div>
            </div>
            <div class="metric">
                <div class="metric-value">{summary.get('risk_score', 0)}</div>
                <div>Risk Score</div>
            </div>
        </div>
        
        <h2>Vulnerability Details</h2>
        {self._generate_vulnerability_html(scan_results)}
        
        <h2>Scan Details</h2>
        {self._generate_scan_details_html(scan_results)}
    </div>
</body>
</html>
            """
            
            return html_content
            
        except Exception as e:
            log.error(f"Failed to generate security report: {e}")
            return "<html><body><h1>Error generating security report</h1></body></html>"
    
    def _generate_vulnerability_html(self, scan_results: Dict[str, Any]) -> str:
        """Generate HTML for vulnerability details.
        
        Args:
            scan_results: Scan results
            
        Returns:
            HTML content
        """
        html = ""
        all_vulnerabilities = []
        
        # Collect all vulnerabilities
        for scan_type, scan_data in scan_results.items():
            if scan_type != 'scan_summary' and isinstance(scan_data, dict) and 'vulnerabilities' in scan_data:
                for vuln in scan_data['vulnerabilities']:
                    vuln['scan_type'] = scan_type
                    all_vulnerabilities.append(vuln)
        
        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_vulnerabilities.sort(key=lambda x: severity_order.get(x.get('severity', 'low').lower(), 3))
        
        for vuln in all_vulnerabilities:
            severity_class = f"severity-{vuln.get('severity', 'low').lower()}"
            html += f"""
            <div class="vulnerability {severity_class}">
                <h3>{vuln.get('type', 'Unknown')}</h3>
                <p><strong>Severity:</strong> {vuln.get('severity', 'Unknown')}</p>
                <p><strong>Endpoint:</strong> {vuln.get('endpoint', 'Unknown')}</p>
                <p><strong>Description:</strong> {vuln.get('description', 'No description')}</p>
                {f'<p><strong>Payload:</strong> <code>{vuln.get("payload", "")}</code></p>' if vuln.get('payload') else ''}
                {f'<p><strong>Method:</strong> {vuln.get("method", "Unknown")}</p>' if vuln.get('method') else ''}
            </div>
            """
        
        return html
    
    def _generate_scan_details_html(self, scan_results: Dict[str, Any]) -> str:
        """Generate HTML for scan details.
        
        Args:
            scan_results: Scan results
            
        Returns:
            HTML content
        """
        html = "<table><tr><th>Scan Type</th><th>Vulnerabilities Found</th><th>Duration</th><th>Status</th></tr>"
        
        for scan_type, scan_data in scan_results.items():
            if scan_type != 'scan_summary' and isinstance(scan_data, dict):
                vuln_count = scan_data.get('vulnerability_count', 0)
                duration = scan_data.get('scan_duration', 0)
                status = "Error" if 'error' in scan_data else "Completed"
                
                html += f"""
                <tr>
                    <td>{scan_type.replace('_', ' ').title()}</td>
                    <td>{vuln_count}</td>
                    <td>{duration:.2f}s</td>
                    <td>{status}</td>
                </tr>
                """
        
        html += "</table>"
        return html
