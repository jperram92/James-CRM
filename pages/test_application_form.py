import unittest
import sqlite3
import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.application_form import (
    get_db_connection,
    fetch_contacts,
    insert_application
)

class TestApplicationForm(unittest.TestCase):
    def setUp(self):
        """Set up test database and sample data"""
        if os.path.exists('test_crm.db'):
            os.remove('test_crm.db')
            
        self.test_db_path = 'test_crm.db'
        self.conn = sqlite3.connect(self.test_db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        # Create tables with proper order for foreign keys
        self.cursor.executescript('''
            PRAGMA foreign_keys = ON;
            
            DROP TABLE IF EXISTS applications;
            DROP TABLE IF EXISTS contacts;
            
            CREATE TABLE contacts (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT
            );
            
            CREATE TABLE applications (
                id INTEGER PRIMARY KEY,
                contact_id INTEGER NOT NULL,
                interest TEXT NOT NULL,
                reason TEXT,
                skillsets TEXT,
                FOREIGN KEY (contact_id) REFERENCES contacts (id)
            );
        ''')
        
        # Insert single test contact
        self.cursor.execute('''
            INSERT INTO contacts (name, email, phone)
            VALUES (?, ?, ?)
        ''', ('Test User', 'test@test.com', '1234567890'))
        self.conn.commit()

    def tearDown(self):
        """Clean up test database"""
        self.conn.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_get_db_connection(self):
        """Test database connection"""
        conn = get_db_connection()
        self.assertIsNotNone(conn)
        self.assertEqual(conn.row_factory, sqlite3.Row)
        conn.close()

    def test_fetch_contacts(self):
        """Test fetching contacts from database"""
        contacts = fetch_contacts()
        self.assertIsNotNone(contacts)
        self.assertEqual(len(contacts), 1)
        
        contact = contacts[0]
        self.assertEqual(contact['name'], 'Test User')
        self.assertEqual(contact['email'], 'test@test.com')
        self.assertEqual(contact['phone'], '1234567890')

    def test_insert_application(self):
        """Test inserting new application"""
        # Get test contact id
        self.cursor.execute('SELECT id FROM contacts WHERE email = ?', ('test@test.com',))
        contact_id = self.cursor.fetchone()['id']
        
        # Test data
        test_data = {
            'interest': 'Python Development',
            'reason': 'Career Growth',
            'skillsets': 'Python, SQL, Testing'
        }
        
        # Insert application
        app_id = insert_application(
            contact_id,
            test_data['interest'],
            test_data['reason'],
            test_data['skillsets']
        )
        
        # Verify insertion
        self.cursor.execute('SELECT * FROM applications WHERE id = ?', (app_id,))
        application = self.cursor.fetchone()
        
        self.assertIsNotNone(application, "Application should be inserted")
        self.assertEqual(application['interest'], test_data['interest'])
        self.assertEqual(application['reason'], test_data['reason'])
        self.assertEqual(application['skillsets'], test_data['skillsets'])

if __name__ == '__main__':
    unittest.main()