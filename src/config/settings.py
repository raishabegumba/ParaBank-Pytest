"""Enterprise configuration management for the test framework."""
import os
import yaml
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from pydantic import Field
try:
    from pydantic import field_validator
except ImportError:
    from pydantic import validator as field_validator
from enum import Enum


class Environment(str, Enum):
    """Supported test environments."""
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"
    QA = "qa"


class BrowserType(str, Enum):
    """Supported browser types."""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


class LogLevel(str, Enum):
    """Supported log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Enterprise application settings loaded from environment variables and config files."""

    # Application URLs
    base_url: str = Field(default="http://localhost:8080/parabank", description="Base application URL")
    api_base_url: str = Field(default="http://localhost:8080/parabank/services/bank", description="API base URL")
    
    # Environment Configuration
    test_env: Environment = Field(default=Environment.DEV, description="Test environment")
    config_file: Optional[str] = Field(default=None, description="Custom config file path")

    # Browser Configuration
    browser: BrowserType = Field(default=BrowserType.CHROMIUM, description="Browser type")
    headless: bool = Field(default=False, description="Run browser in headless mode")
    window_width: int = Field(default=1920, description="Browser window width")
    window_height: int = Field(default=1080, description="Browser window height")
    
    # Mobile/Responsive Testing
    mobile_viewport: bool = Field(default=False, description="Enable mobile viewport")
    device_scale_factor: int = Field(default=1, description="Device scale factor")
    
    # Network Configuration
    slow_mo: int = Field(default=0, description="Slow down operations by ms")
    ignore_https_errors: bool = Field(default=False, description="Ignore HTTPS errors")

    # Playwright Configuration
    implicit_wait: int = Field(default=10000, description="Implicit wait in ms")
    explicit_wait: int = Field(default=20000, description="Explicit wait in ms")
    page_load_timeout: int = Field(default=30000, description="Page load timeout in ms")
    navigation_timeout: int = Field(default=30000, description="Navigation timeout in ms")
    
    # Test Execution Configuration
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, description="Delay between retries in seconds")
    flaky_test_threshold: int = Field(default=3, description="Flaky test failure threshold")
    
    # Parallel Execution
    parallel_workers: int = Field(default=4, description="Number of parallel workers")
    parallel_scope: str = Field(default="function", description="Parallel execution scope")

    # Logging Configuration
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    log_to_file: bool = Field(default=True, description="Enable file logging")
    log_rotation: str = Field(default="500 MB", description="Log rotation size")
    log_retention: str = Field(default="10 days", description="Log retention period")
    
    # Reporting Configuration
    report_format: str = Field(default="html", description="Report format")
    allure_report_dir: str = Field(default="reports/allure", description="Allure report directory")
    html_report_dir: str = Field(default="reports/html", description="HTML report directory")
    screenshot_on_failure: bool = Field(default=True, description="Take screenshot on failure")
    video_recording: bool = Field(default=False, description="Enable video recording")
    trace_recording: bool = Field(default=False, description="Enable trace recording")
    
    # Test Data Configuration
    test_data_dir: str = Field(default="test_data", description="Test data directory")
    generate_test_data: bool = Field(default=True, description="Auto-generate test data")
    cleanup_test_data: bool = Field(default=True, description="Cleanup test data after tests")

    # Test Credentials (with validation)
    test_username: str = Field(default="testuser", description="Test username")
    test_password: str = Field(default="testpass", description="Test password")
    admin_username: str = Field(default="admin", description="Admin username")
    admin_password: str = Field(default="admin", description="Admin password")
    
    # Feature Flags
    enable_api_testing: bool = Field(default=True, description="Enable API testing")
    enable_ui_testing: bool = Field(default=True, description="Enable UI testing")
    enable_performance_testing: bool = Field(default=False, description="Enable performance testing")
    enable_security_testing: bool = Field(default=False, description="Enable security testing")
    
        
    def load_config_file(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML or JSON file."""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            if config_file.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            elif config_file.suffix.lower() == '.json':
                return json.load(f)
            else:
                raise ValueError(f"Unsupported config file format: {config_file.suffix}")
    
    def get_env_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration."""
        env_config_file = Path(f"config/environments/{self.test_env.value}.yaml")
        if env_config_file.exists():
            return self.load_config_file(str(env_config_file))
        return {}
    
    def get_test_data_config(self) -> Dict[str, Any]:
        """Get test data configuration."""
        test_data_config_file = Path("config/test_data.yaml")
        if test_data_config_file.exists():
            return self.load_config_file(str(test_data_config_file))
        return {}

    # Security Configuration
    encrypt_credentials: bool = Field(default=True, description="Encrypt test credentials")
    mask_sensitive_data: bool = Field(default=True, description="Mask sensitive data in logs")
    security_scan_enabled: bool = Field(default=False, description="Enable security scanning")
    
    # API Testing Configuration
    api_timeout: int = Field(default=30000, description="API request timeout in ms")
    api_retry_attempts: int = Field(default=3, description="API retry attempts")
    validate_api_schema: bool = Field(default=True, description="Validate API schema")
    
    # Performance Testing
    performance_threshold: float = Field(default=3.0, description="Performance threshold in seconds")
    memory_threshold: int = Field(default=500, description="Memory threshold in MB")
    
    # Database Configuration (for future use)
    db_host: Optional[str] = Field(default=None, description="Database host")
    db_port: Optional[int] = Field(default=None, description="Database port")
    db_name: Optional[str] = Field(default=None, description="Database name")
    db_user: Optional[str] = Field(default=None, description="Database user")
    db_password: Optional[str] = Field(default=None, description="Database password")
    
    # CI/CD Configuration
    ci_environment: bool = Field(default=False, description="Running in CI environment")
    artifact_retention_days: int = Field(default=30, description="Artifact retention days")

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"  # Allow extra fields for future extensibility
    
    def __init__(self, **data):
        """Initialize settings with config file support."""
        super().__init__(**data)
        
        # Load environment-specific config if available
        if self.config_file:
            env_config = self.load_config_file(self.config_file)
            for key, value in env_config.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        else:
            # Load default environment config
            env_config = self.get_env_config()
            for key, value in env_config.items():
                if hasattr(self, key):
                    setattr(self, key, value)
    
    def get_database_url(self) -> Optional[str]:
        """Construct database URL from components."""
        if all([self.db_host, self.db_port, self.db_name, self.db_user]):
            return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        return None
    
    def is_ci_environment(self) -> bool:
        """Check if running in CI environment."""
        return self.ci_environment or bool(os.getenv('CI', os.getenv('GITHUB_ACTIONS', os.getenv('JENKINS_URL'))))
    
    def get_report_paths(self) -> Dict[str, str]:
        """Get all report paths."""
        return {
            'allure': self.allure_report_dir,
            'html': self.html_report_dir,
            'screenshots': 'reports/screenshots',
            'videos': 'reports/videos',
            'traces': 'reports/traces',
            'logs': 'logs'
        }


# Global settings instance with lazy loading
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance (singleton pattern)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# For backward compatibility
settings = get_settings()
