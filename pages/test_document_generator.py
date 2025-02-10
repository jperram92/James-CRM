import unittest
import sqlite3
import os
import sys
from io import BytesIO
from PIL import Image
from datetime import datetime
import warnings
import streamlit as st
warnings.filterwarnings('ignore', category=UserWarning)
st.set_page_config = lambda **kwargs: None
from document_generator import (
    get_db_connection,
    save_signature_to_db,
    fetch_signature_from_db,
    fetch_contact_with_application,
    create_document
)

class TestDocumentGenerator(unittest.TestCase):
    def setUp(self):
        # Create test database
        self.conn = sqlite3.connect('test_crm.db')
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        # Drop existing tables if they exist
        self.cursor.executescript('''
            DROP TABLE IF EXISTS application_documents;
            DROP TABLE IF EXISTS applications;
            DROP TABLE IF EXISTS contacts;
        ''')
        
        # Create tables
        self.cursor.executescript('''
            CREATE TABLE contacts (
                id INTEGER PRIMARY KEY,
                email TEXT,
                phone TEXT,
                name TEXT
            );
            
            CREATE TABLE applications (
                id INTEGER PRIMARY KEY,
                contact_id INTEGER,
                interest TEXT,
                reason TEXT,
                skillsets TEXT,
                FOREIGN KEY (contact_id) REFERENCES contacts (id)
            );
            
            CREATE TABLE application_documents (
                id INTEGER PRIMARY KEY,
                contact_id INTEGER,
                document_name TEXT,
                signature BLOB,
                timestamp TEXT,
                FOREIGN KEY (contact_id) REFERENCES contacts (id)
            );
        ''')
        
        # Insert test data
        self.cursor.execute('''
            INSERT INTO contacts (id, email, phone, name)
            VALUES (?, ?, ?, ?)
        ''', (1, 'test@test.com', '1234567890', 'Test User'))
        
        self.cursor.execute('''
            INSERT INTO applications (contact_id, interest, reason, skillsets)
            VALUES (?, ?, ?, ?)
        ''', (1, 'Developer', 'Test reason', 'Python, SQL'))
        
        self.conn.commit()

    def tearDown(self):
        self.conn.close()
        if os.path.exists('test_crm.db'):
            os.remove('test_crm.db')

    def test_get_db_connection(self):
        conn = get_db_connection()
        self.assertIsNotNone(conn)
        self.assertEqual(conn.row_factory, sqlite3.Row)
        conn.close()

    def test_save_and_fetch_signature(self):
        # Create a simple test image
        img = Image.new('RGB', (60, 30), color='red')
        test_contact_id = 1
        
        # Save signature
        save_signature_to_db(test_contact_id, img)
        
        # Fetch signature
        fetched_signature = fetch_signature_from_db(test_contact_id)
        
        self.assertIsNotNone(fetched_signature)
        self.assertIsInstance(fetched_signature, BytesIO)

    def test_fetch_contact_with_application(self):
        """Test fetching contact data with associated application"""
        try:
            # Verify contact exists
            self.cursor.execute('SELECT * FROM contacts WHERE id = 1')
            contact = self.cursor.fetchone()
            self.assertIsNotNone(contact, "Test contact not found")
            print(f"DEBUG: Contact found: {dict(contact)}")
            
            # Verify application exists
            self.cursor.execute('SELECT * FROM applications WHERE contact_id = 1')
            application = self.cursor.fetchone()
            self.assertIsNotNone(application, "Test application not found")
            print(f"DEBUG: Application found: {dict(application)}")
            
            # Test the actual function
            contact_data = fetch_contact_with_application(1)
            print(f"DEBUG: Fetched contact data: {contact_data}")
            
            # Basic assertions
            self.assertIsNotNone(contact_data, "Contact data should not be None")
            
            # Contact data assertions
            expected_contact_data = {
                'name': 'Test User',
                'email': 'test@test.com',
                'phone': '1234567890',
                'interest': 'Developer',
                'reason': 'Test reason',
                'skillsets': 'Python, SQL'
            }
            
            for key, value in expected_contact_data.items():
                self.assertEqual(
                    contact_data[key], 
                    value, 
                    f"Mismatch in {key}: expected '{value}', got '{contact_data.get(key)}'"
                )
                
        except Exception as e:
            print(f"Test failed with error: {str(e)}")
            raise

    def test_create_document(self):
        # Test document creation
        pdf_output = create_document(
            contact_name="Test User",
            contact_email="test@test.com",
            contact_phone="1234567890",
            document_name="Test Document",
            interest="Developer",
            reason="Test reason",
            skillsets="Python, SQL"
        )
        
        self.assertIsNotNone(pdf_output)
        self.assertIsInstance(pdf_output, BytesIO)
        self.assertTrue(pdf_output.getvalue().startswith(b'%PDF'))

    def test_create_document_with_special_characters(self):
        """Test document creation with special characters in input"""
        pdf_output = create_document(
            contact_name="Test User @#$%",
            contact_email="test@test.com",
            contact_phone="1234567890",
            document_name="Test Doc !@#",
            interest="Dev & QA",
            reason="Test reason (123)",
            skillsets="Python, C++, Java;"
        )
        self.assertIsNotNone(pdf_output)
        self.assertTrue(pdf_output.getvalue().startswith(b'%PDF'))

    def test_fetch_signature_nonexistent_contact(self):
        """Test fetching signature for non-existent contact"""
        signature = fetch_signature_from_db(999)
        self.assertIsNone(signature)

if __name__ == '__main__':
    unittest.main()