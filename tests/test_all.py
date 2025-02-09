import pytest
import sqlite3
import pandas as pd
from datetime import datetime, date
import os
import sys
from unittest.mock import patch, MagicMock

# Add the project root directory to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Import mock streamlit before other imports
from .mock_streamlit import mock_st, mock_components, mock_canvas

# Import test-safe modules first
from pages.application_form import (
    get_db_connection, 
    fetch_contacts, 
    insert_application
)
from pages.budgets import (
    create_budget, 
    update_budget, 
    get_budgets_for_contact, 
    delete_budget, 
    get_contacts
)
from pages.budget_line_items import (
    create_budget_line_item, 
    validate_budget_allocation
)
from pages.document_generator import (
    fetch_contact_with_application, 
    create_document
)
from pages.crm_contact_app import insert_contact  # Add this import

@pytest.fixture(scope="session")
def test_db():
    """Set up test database"""
    from .setup_test_db import setup_test_database
    db_path = os.path.join(PROJECT_ROOT, 'test_crm.db')
    conn = setup_test_database(db_path)
    yield db_path
    conn.close()
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture(autouse=True)
def setup_test_env(test_db):
    # Override the database connection for testing
    global get_db_connection
    original_get_db_connection = get_db_connection
    get_db_connection = lambda: sqlite3.connect(test_db)
    
    yield
    
    # Restore original database connection
    get_db_connection = original_get_db_connection

@pytest.fixture(autouse=True)
def cleanup_db(test_db):
    """Clean up database after each test"""
    yield
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts")
    cursor.execute("DELETE FROM budgets")
    cursor.execute("DELETE FROM budget_line_items")
    cursor.execute("DELETE FROM applications")
    conn.commit()
    conn.close()

@pytest.fixture
def sample_contact():
    return {
        'title': 'Mr.',
        'gender': 'Male',
        'name': 'Test User',
        'email': 'test@example.com',
        'phone': '1234567890',
        'message': 'Test message',
        'address_line': 'Test Address',
        'suburb': 'Test Suburb',
        'postcode': '12345',
        'state': 'NSW',
        'country': 'Australia'
    }

class TestDatabaseConnection:
    def test_db_connection(self, test_db):
        conn = get_db_connection()
        assert conn is not None
        conn.close()

class TestBudgetManagement:
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        self.test_budget = {
            'contact_id': 1,
            'budget_name': 'Test Budget',
            'total_budget': 1000.00,
            'start_date': '2025-01-01',
            'end_date': '2025-12-31',
            'currency': 'USD'
        }
        # Create a test contact first
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO contacts (name, email) 
            VALUES (?, ?)
        ''', ('Test User', 'test@example.com'))
        conn.commit()
        conn.close()

    def test_create_budget(self):
        result = create_budget(**self.test_budget)
        assert result is None

    def test_update_budget(self):
        # First create a budget
        create_budget(**self.test_budget)
        result = update_budget(1, budget_name='Updated Budget')
        assert result is None

    def test_get_budgets_for_contact(self):
        # First create a budget
        create_budget(**self.test_budget)
        budgets = get_budgets_for_contact(1)
        assert isinstance(budgets, list)
        assert len(budgets) > 0

class TestBudgetLineItems:
    def setup_method(self):
        self.test_line_item = {
            'budget_id': 1,
            'line_item_name': 'Test Line Item',
            'allocated_amount': 500.00
        }

    def test_create_budget_line_item(self):
        result = create_budget_line_item(**self.test_line_item)
        assert isinstance(result, int)

    def test_validate_budget_allocation(self):
        result = validate_budget_allocation(1, 500.00)
        assert result is True

class TestApplicationForm:
    def setup_method(self):
        self.test_application = {
            'contact_id': 1,
            'interest': 'Test Interest',
            'reason': 'Test Reason',
            'skillsets': 'Test Skills'
        }

    def test_insert_application(self):
        result = insert_application(**self.test_application)
        assert result is None

    def test_fetch_contacts(self, sample_contact, test_db):
        # First insert a contact
        insert_contact(**sample_contact)
        contacts = fetch_contacts()
        assert len(contacts) > 0

class TestDocumentGeneration:
    def test_fetch_contact_with_application(self):
        result = fetch_contact_with_application(1)
        assert isinstance(result, (dict, type(None)))

    def test_create_document(self):
        result = create_document(
            contact_name='Test User',
            contact_email='test@example.com',
            contact_phone='1234567890',
            document_name='Test Document',
            interest='Test Interest',
            reason='Test Reason',
            skillsets='Test Skills'
        )
        assert result is not None

class TestBasicFunctionality:
    def test_db_connection(self, test_db):
        """Test database connection works"""
        conn = get_db_connection()
        assert conn is not None
        conn.close()

    def test_create_budget(self, test_db):
        """Test budget creation"""
        # Create test contact first
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO contacts (name, email) 
            VALUES (?, ?)
        ''', ('Test User', 'test@example.com'))
        conn.commit()
        conn.close()

        # Test budget creation
        budget_data = {
            'contact_id': 1,
            'budget_name': 'Test Budget',
            'total_budget': 1000.00,
            'start_date': '2025-01-01',
            'end_date': '2025-12-31'
        }
        result = create_budget(**budget_data)
        assert result is None

    def test_create_budget_line_item(self, test_db):
        """Test budget line item creation"""
        line_item = {
            'budget_id': 1,
            'line_item_name': 'Test Item',
            'allocated_amount': 500.00
        }
        result = create_budget_line_item(**line_item)
        assert result is not None