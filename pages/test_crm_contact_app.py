import unittest
import sqlite3
import os
import sys
import re
from unittest.mock import MagicMock
import streamlit as st
import warnings

warnings.filterwarnings('ignore', category=Warning)

# Mock Streamlit functions
st.set_page_config = lambda **kwargs: None
st.session_state = {}

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.crm_contact_app import (
    is_valid_email,
    get_db_connection,
    insert_contact,
    update_contact,
    delete_contact,
    search_contact_by_name
)

class TestCRMContactApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        # Ensure we're using test database
        os.environ['TESTING'] = 'true'

    def setUp(self):
        """Set up fresh database for each test"""
        # Remove existing test database
        if os.path.exists('test_crm.db'):
            os.remove('test_crm.db')

        self.conn = sqlite3.connect('test_crm.db')
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        # Create contacts table
        self.cursor.execute('''
            CREATE TABLE contacts (
                id INTEGER PRIMARY KEY,
                title TEXT,
                gender TEXT,
                name TEXT,
                email TEXT UNIQUE,
                phone TEXT,
                message TEXT,
                address_line TEXT,
                suburb TEXT,
                postcode TEXT,
                state TEXT,
                country TEXT
            )
        ''')
        self.conn.commit()

    def tearDown(self):
        """Clean up after each test"""
        self.conn.close()
        if os.path.exists('test_crm.db'):
            os.remove('test_crm.db')

    def test_is_valid_email(self):
        """Test email validation function"""
        self.assertTrue(is_valid_email("test@example.com"))
        self.assertFalse(is_valid_email("invalid-email"))
        self.assertFalse(is_valid_email(None))

        # Mock email to simulate Streamlit input
        mock_email = MagicMock()
        mock_email._mock_return_value = True
        self.assertTrue(is_valid_email(mock_email))

    def test_get_db_connection(self):
        """Test database connection function"""
        conn = get_db_connection()
        self.assertIsNotNone(conn)
        self.assertEqual(conn.row_factory, sqlite3.Row)
        conn.close()

    def test_insert_contact(self):
        """Test contact insertion function"""
        title = "Mr."
        gender = "Male"
        name = "Test User"
        email = "test@example.com"
        phone = "1234567890"
        message = "Test message"
        address_line = "Test address"
        suburb = "Test suburb"
        postcode = "1234"
        state = "Test state"
        country = "Test country"

        result = insert_contact(title, gender, name, email, phone, message, address_line, suburb, postcode, state, country)
        self.assertTrue(result)

        # Verify contact was created
        self.cursor.execute('SELECT * FROM contacts WHERE email = ?', (email,))
        contact = self.cursor.fetchone()
        self.assertIsNotNone(contact)
        self.assertEqual(contact['name'], name)

        # Test with invalid email
        invalid_email = "invalid-email"
        result = insert_contact(title, gender, name, invalid_email, phone, message, address_line, suburb, postcode, state, country)
        self.assertFalse(result)

    def test_update_contact(self):
        """Test contact update function"""
        # First insert a contact
        title = "Mr."
        gender = "Male"
        name = "Test User"
        email = "test@example.com"
        phone = "1234567890"
        message = "Test message"
        address_line = "Test address"
        suburb = "Test suburb"
        postcode = "1234"
        state = "Test state"
        country = "Test country"

        insert_contact(title, gender, name, email, phone, message, address_line, suburb, postcode, state, country)

        # Get the contact ID
        self.cursor.execute('SELECT id FROM contacts WHERE email = ?', (email,))
        contact_id = self.cursor.fetchone()['id']

        # Update the contact
        new_name = "Updated User"
        result = update_contact(contact_id, title, gender, new_name, email, phone, message, address_line, suburb, postcode, state, country)
        self.assertTrue(result)

        # Verify contact was updated
        self.cursor.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
        contact = self.cursor.fetchone()
        self.assertEqual(contact['name'], new_name)

        # Test with invalid email
        invalid_email = "invalid-email"
        result = update_contact(contact_id, title, gender, new_name, invalid_email, phone, message, address_line, suburb, postcode, state, country)
        self.assertFalse(result)

    def test_delete_contact(self):
        """Test contact deletion function"""
        # First insert a contact
        title = "Mr."
        gender = "Male"
        name = "Test User"
        email = "test@example.com"
        phone = "1234567890"
        message = "Test message"
        address_line = "Test address"
        suburb = "Test suburb"
        postcode = "1234"
        state = "Test state"
        country = "Test country"

        insert_contact(title, gender, name, email, phone, message, address_line, suburb, postcode, state, country)

        # Get the contact ID
        self.cursor.execute('SELECT id FROM contacts WHERE email = ?', (email,))
        contact_id = self.cursor.fetchone()['id']

        # Delete the contact
        delete_contact(contact_id)

        # Verify contact was deleted
        self.cursor.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
        contact = self.cursor.fetchone()
        self.assertIsNone(contact)

    def test_search_contact_by_name(self):
        """Test contact search function"""
        # Insert some contacts
        insert_contact("Mr.", "Male", "Test User 1", "test1@example.com", "1234567890", "Test message", "Test address", "Test suburb", "1234", "Test state", "Test country")
        insert_contact("Ms.", "Female", "Test User 2", "test2@example.com", "0987654321", "Test message", "Test address", "Test suburb", "1234", "Test state", "Test country")

        # Search for contacts
        search_results = search_contact_by_name("Test User 1")
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0]['email'], "test1@example.com")

        search_results = search_contact_by_name("NonExistent User")
        self.assertEqual(len(search_results), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)