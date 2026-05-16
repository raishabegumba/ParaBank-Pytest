"""
Test data for ParaBank registration module.
All usernames are dynamically generated to ensure test isolation.
"""

import uuid


def generate_username(prefix="testuser"):
    """Generate a unique username for each test run."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


# -----------------------------
# VALID USER DATA
# -----------------------------
def get_valid_user():
    return {
        "first_name": "Test",
        "last_name": "User",
        "address": "123 Street",
        "city": "New York",
        "state": "NY",
        "zip_code": "12345",
        "phone": "5551234567",
        "ssn": "123456789",
        "username": generate_username(),
        "password": "Password123!",
        "confirm_password": "Password123!"
    }


# -----------------------------
# INVALID USER DATA
# -----------------------------
def get_invalid_users():
    base_user = get_valid_user()

    return {
        "empty_username": {
            **base_user,
            "username": ""
        },

        "weak_password": {
            **base_user,
            "username": generate_username(),
            "password": "123",
            "confirm_password": "123"
        },

        "password_mismatch": {
            **base_user,
            "username": generate_username(),
            "password": "Password123!",
            "confirm_password": "Different123!"
        },

        "invalid_zip": {
            **base_user,
            "username": generate_username(),
            "zip_code": "12AB"
        },

        "invalid_phone": {
            **base_user,
            "username": generate_username(),
            "phone": "abc123"
        },

        "invalid_ssn": {
            **base_user,
            "username": generate_username(),
            "ssn": "12"
        }
    }


# -----------------------------
# EDGE CASE DATA
# -----------------------------
def get_edge_users():
    return {
        "long_username": {
            **get_valid_user(),
            "username": "a" * 60
        },

        "special_char_name": {
            **get_valid_user(),
            "username": generate_username(),
            "first_name": "John-O'Connor",
            "last_name": "Smith-Jones"
        },

        "max_length_username": {
            **get_valid_user(),
            "username": "u" * 50
        }
    }


# -----------------------------
# SECURITY DATA PLACEHOLDER
# -----------------------------
SECURITY_PAYLOADS = [
    "<script>alert(1)</script>",
    "' OR '1'='1",
    "admin'--",
    "<img src=x onerror=alert(1)>",
    "javascript:alert(1)"
]