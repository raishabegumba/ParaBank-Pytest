"""Base class for API testing."""
import requests
from typing import Optional, Dict, Any
from src.config.settings import settings
from src.config.logger import log


class BaseAPI:
    """Base API class with common functionality for all API tests."""

    def __init__(self, base_url: Optional[str] = None):
        """Initialize API client."""
        # Some environments may not expose a dedicated JSON REST API.
        # If api_base_url points to a non-existing API namespace, callers should
        # override base_url in tests. We keep the default as-is.
        self.base_url = base_url or settings.api_base_url
        self.session = requests.Session()
        self.log = log
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def get(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> requests.Response:
        """Send GET request."""
        url = f"{self.base_url}{endpoint}"
        headers = headers or self.headers
        try:
            response = self.session.get(url, params=params, headers=headers, **kwargs)
            self.log.info(f"GET {url} - Status: {response.status_code}")
            return response
        except Exception as e:
            self.log.error(f"GET request failed: {e}")
            raise

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> requests.Response:
        """Send POST request."""
        url = f"{self.base_url}{endpoint}"
        headers = headers or self.headers
        try:
            response = self.session.post(url, data=data, json=json, headers=headers, **kwargs)
            self.log.info(f"POST {url} - Status: {response.status_code}")
            return response
        except Exception as e:
            self.log.error(f"POST request failed: {e}")
            raise

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> requests.Response:
        """Send PUT request."""
        url = f"{self.base_url}{endpoint}"
        headers = headers or self.headers
        try:
            response = self.session.put(url, data=data, json=json, headers=headers, **kwargs)
            self.log.info(f"PUT {url} - Status: {response.status_code}")
            return response
        except Exception as e:
            self.log.error(f"PUT request failed: {e}")
            raise

    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> requests.Response:
        """Send DELETE request."""
        url = f"{self.base_url}{endpoint}"
        headers = headers or self.headers
        try:
            response = self.session.delete(url, headers=headers, **kwargs)
            self.log.info(f"DELETE {url} - Status: {response.status_code}")
            return response
        except Exception as e:
            self.log.error(f"DELETE request failed: {e}")
            raise

    def set_bearer_token(self, token: str):
        """Set authorization bearer token."""
        self.headers["Authorization"] = f"Bearer {token}"
        self.log.info("Bearer token set in headers")

    def set_headers(self, headers: Dict):
        """Set custom headers."""
        self.headers.update(headers)
        self.log.info(f"Headers updated: {headers}")

    def close_session(self):
        """Close the session."""
        self.session.close()
        self.log.info("API session closed")
