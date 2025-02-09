import re
from unittest.mock import MagicMock

def mock_is_valid_email(email):
    """Mock email validation that always returns True for testing"""
    if isinstance(email, MagicMock):
        return True
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None