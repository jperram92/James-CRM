import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Mock streamlit before any imports
mock_st = MagicMock()
mock_st.success = MagicMock()
mock_st.error = MagicMock()
mock_st.warning = MagicMock()
mock_st.info = MagicMock()
mock_st.write = MagicMock()
mock_st.markdown = MagicMock()
mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock()])
mock_st.form = MagicMock()
mock_st.session_state = {}
mock_st.sidebar = MagicMock()
mock_st.set_page_config = MagicMock()

sys.modules['streamlit'] = mock_st

# Mock SMTP settings
mock_smtp = MagicMock()
mock_smtp.return_value.starttls.return_value = None
mock_smtp.return_value.login.return_value = None
mock_smtp.return_value.sendmail.return_value = None
mock_smtp.return_value.quit.return_value = None

@pytest.fixture(scope="session", autouse=True)
def mock_dependencies():
    """Mock all external dependencies"""
    with patch('smtplib.SMTP', mock_smtp):
        yield

@pytest.fixture(scope="session")
def test_db():
    """Set up test database"""
    from .setup_test_db import setup_test_database
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_crm.db')
    conn = setup_test_database(db_path)
    yield db_path
    conn.close()
    if os.path.exists(db_path):
        os.remove(db_path)