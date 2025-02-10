import unittest
import sqlite3
import os
import sys
from datetime import date
import warnings
import streamlit as st
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Suppress all warnings
warnings.filterwarnings('ignore', category=Warning)

# Mock Streamlit functions
st.set_page_config = lambda **kwargs: None
st.session_state = {}

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.budget_line_items import (
    get_db_connection,
    create_budget_line_item,
    create_product
)

class TestBudgetLineItems(unittest.TestCase):
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
        
        # Create tables with proper constraints
        self.cursor.executescript('''
            PRAGMA foreign_keys = ON;
            
            CREATE TABLE contacts (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT
            );
            
            CREATE TABLE budgets (
                id INTEGER PRIMARY KEY,
                contact_id INTEGER NOT NULL,
                budget_name TEXT NOT NULL,
                total_budget REAL NOT NULL,
                current_spent REAL DEFAULT 0,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                currency TEXT NOT NULL,
                status TEXT DEFAULT 'Active',
                FOREIGN KEY (contact_id) REFERENCES contacts (id)
            );

            CREATE TABLE budget_line_items (
                id INTEGER PRIMARY KEY,
                budget_id INTEGER NOT NULL,
                line_item_name TEXT NOT NULL,
                allocated_amount REAL NOT NULL,
                FOREIGN KEY (budget_id) REFERENCES budgets (id)
            );

            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                line_item_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                product_group TEXT,
                rate REAL,
                frequency TEXT,
                service_name TEXT,
                description TEXT,
                FOREIGN KEY (line_item_id) REFERENCES budget_line_items (id)
            );
        ''')
        
        # Insert test contact
        self.cursor.execute('''
            INSERT INTO contacts (name, email, phone)
            VALUES (?, ?, ?)
        ''', ('Test User', 'test@test.com', '1234567890'))
        self.test_contact_id = self.cursor.lastrowid
        
        # Insert test budget
        self.cursor.execute('''
            INSERT INTO budgets (contact_id, budget_name, total_budget, start_date, end_date, currency)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.test_contact_id, 'Test Budget', 1000.00, '2025-01-01', '2025-12-31', 'USD'))
        self.test_budget_id = self.cursor.lastrowid
        
        self.conn.commit()

    def tearDown(self):
        """Clean up after each test"""
        self.conn.close()
        if os.path.exists('test_crm.db'):
            os.remove('test_crm.db')

    def test_create_budget_line_item(self):
        """Test budget line item creation"""
        line_item_name = 'Test Line Item'
        allocated_amount = 500.00
        
        create_budget_line_item(self.test_budget_id, line_item_name, allocated_amount)
        
        # Verify line item was created
        self.cursor.execute('SELECT * FROM budget_line_items WHERE budget_id = ?', (self.test_budget_id,))
        line_item = self.cursor.fetchone()
        self.assertIsNotNone(line_item)
        self.assertEqual(line_item['line_item_name'], line_item_name)
        self.assertEqual(line_item['allocated_amount'], allocated_amount)

    def test_create_budget_line_item_exceeding_budget(self):
        """Test creating line item exceeding budget total"""
        line_item_name = 'Expensive Item'
        allocated_amount = 2000.00  # More than budget total of 1000.00
        
        with self.assertRaises(Exception):
            create_budget_line_item(self.test_budget_id, line_item_name, allocated_amount)

    def test_create_product(self):
        """Test product creation"""
        # First create a budget line item
        self.cursor.execute('''
            INSERT INTO budget_line_items (budget_id, line_item_name, allocated_amount)
            VALUES (?, ?, ?)
        ''', (self.test_budget_id, 'Test Line Item', 500.00))
        line_item_id = self.cursor.lastrowid
        self.conn.commit()
        
        # Create a product
        product_name = 'Test Product'
        product_group = 'Test Group'
        rate = 100.00
        frequency = 'Monthly'
        service_name = 'Test Service'
        description = 'Test Description'
        
        create_product(line_item_id, product_name, product_group, rate, frequency, service_name, description)
        
        # Verify product was created
        self.cursor.execute('SELECT * FROM products WHERE line_item_id = ?', (line_item_id,))
        product = self.cursor.fetchone()
        self.assertIsNotNone(product)
        self.assertEqual(product['product_name'], product_name)
        self.assertEqual(product['product_group'], product_group)
        self.assertEqual(product['rate'], rate)
        self.assertEqual(product['frequency'], frequency)
        self.assertEqual(product['service_name'], service_name)
        self.assertEqual(product['description'], description)

    def test_create_product_with_zero_rate(self):
        """Test creating product with zero rate"""
        self.cursor.execute('''
            INSERT INTO budget_line_items (budget_id, line_item_name, allocated_amount)
            VALUES (?, ?, ?)
        ''', (self.test_budget_id, 'Test Line Item', 500.00))
        line_item_id = self.cursor.lastrowid
        
        create_product(line_item_id, "Free Product", "Free", 0.00, "One-time", "Free Service", "No cost product")
        
        self.cursor.execute('SELECT * FROM products WHERE line_item_id = ?', (line_item_id,))
        product = self.cursor.fetchone()
        self.assertEqual(product['rate'], 0.00)

if __name__ == '__main__':
    unittest.main(verbosity=2)