import unittest
import sqlite3
import os
import sys
from datetime import date
import warnings
import streamlit as st
import logging
from logging_config import configure_logging

configure_logging()

# Suppress all warnings
warnings.filterwarnings('ignore', category=Warning)

# Mock Streamlit functions
st.set_page_config = lambda **kwargs: None
st.session_state = {}

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.budgets import (
    get_db_connection,
    get_contacts,
    create_budget,
    update_budget,
    get_budgets_for_contact,
    delete_budget
)

class TestBudgets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        # Ensure we're using test database
        os.environ['TESTING'] = 'true'
        
    def setUp(self):
        """Set up fresh database for each test"""
        # Use in-memory database for testing
        self.conn = sqlite3.connect(':memory:')
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
        ''')
        
        # Insert test contact
        self.cursor.execute('''
            INSERT INTO contacts (name, email, phone)
            VALUES (?, ?, ?)
        ''', ('Test User', 'test@test.com', '1234567890'))
        self.test_contact_id = self.cursor.lastrowid
        self.conn.commit()

    def tearDown(self):
        """Clean up after each test"""
        self.conn.close()

    def test_get_db_connection(self):
        """Test database connection"""
        conn = get_db_connection()
        self.assertIsNotNone(conn)
        self.assertEqual(conn.row_factory, sqlite3.Row)
        conn.close()

    def test_get_contacts(self):
        """Test fetching contacts"""
        contacts = get_contacts()
        logger.debug(f"Found {len(contacts)} contacts: {contacts}")
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0]['name'], 'Test User')
        self.assertEqual(contacts[0]['email'], 'test@test.com')

    def test_create_budget(self):
        """Test budget creation"""
        budget_data = {
            'budget_name': 'Test Budget',
            'total_budget': 1000.00,
            'start_date': date(2025, 1, 1),
            'end_date': date(2025, 12, 31),
            'currency': 'USD'
        }
        
        create_budget(
            self.test_contact_id,
            budget_data['budget_name'],
            budget_data['total_budget'],
            budget_data['start_date'],
            budget_data['end_date'],
            budget_data['currency']
        )
        
        # Verify budget was created
        self.cursor.execute('SELECT * FROM budgets WHERE contact_id = ?', (self.test_contact_id,))
        budget = self.cursor.fetchone()
        self.assertIsNotNone(budget)
        self.assertEqual(budget['budget_name'], budget_data['budget_name'])
        self.assertEqual(budget['total_budget'], budget_data['total_budget'])
        self.assertEqual(budget['currency'], budget_data['currency'])

    def test_create_budget_with_past_dates(self):
        """Test creating budget with past dates"""
        with self.assertRaises(ValueError):
            create_budget(
                self.test_contact_id,
                "Past Budget",
                1000.00,
                date(2020, 1, 1),
                date(2020, 12, 31),
                "USD"
            )

    def test_create_budget_with_zero_amount(self):
        """Test creating budget with zero total amount"""
        with self.assertRaises(ValueError):
            create_budget(
                self.test_contact_id,
                "Zero Budget",
                0.00,
                date(2025, 1, 1),
                date(2025, 12, 31),
                "USD"
            )

    def test_create_budget_with_end_date_before_start_date(self):
        """Test creating budget with invalid date range"""
        with self.assertRaises(ValueError):
            create_budget(
                self.test_contact_id,
                "Invalid Dates Budget",
                1000.00,
                date(2025, 12, 31),
                date(2025, 1, 1),
                "USD"
            )

    def test_create_budget_with_invalid_currency(self):
        """Test creating budget with invalid currency code"""
        with self.assertRaises(ValueError):
            create_budget(
                self.test_contact_id,
                "Invalid Currency Budget",
                1000.00,
                date(2025, 1, 1),
                date(2025, 12, 31),
                "INVALID"
            )

    def test_update_budget(self):
        """Test budget update"""
        # First create a budget
        self.cursor.execute('''
            INSERT INTO budgets (contact_id, budget_name, total_budget, start_date, end_date, currency)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.test_contact_id, 'Initial Budget', 1000.00, '2025-01-01', '2025-12-31', 'USD'))
        budget_id = self.cursor.lastrowid
        self.conn.commit()
        
        # Update the budget
        new_name = 'Updated Budget'
        new_total = 2000.00
        update_budget(budget_id, budget_name=new_name, total_budget=new_total)
        
        # Verify update
        self.cursor.execute('SELECT * FROM budgets WHERE id = ?', (budget_id,))
        budget = self.cursor.fetchone()
        self.assertEqual(budget['budget_name'], new_name)
        self.assertEqual(budget['total_budget'], new_total)

    def test_update_budget_status(self):
        """Test updating budget status"""
        self.cursor.execute('''
            INSERT INTO budgets (contact_id, budget_name, total_budget, start_date, end_date, currency)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.test_contact_id, 'Active Budget', 1000.00, '2025-01-01', '2025-12-31', 'USD'))
        budget_id = self.cursor.lastrowid
        
        update_budget(budget_id, status='Completed')
        
        self.cursor.execute('SELECT status FROM budgets WHERE id = ?', (budget_id,))
        status = self.cursor.fetchone()['status']
        self.assertEqual(status, 'Completed')

    def test_update_budget_current_spent(self):
        """Test updating budget's current spent amount"""
        self.cursor.execute('''
            INSERT INTO budgets (contact_id, budget_name, total_budget, current_spent, start_date, end_date, currency)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (self.test_contact_id, 'Spending Budget', 1000.00, 0.00, '2025-01-01', '2025-12-31', 'USD'))
        budget_id = self.cursor.lastrowid
        self.conn.commit()
        
        update_budget(budget_id, current_spent=500.00)
        
        self.cursor.execute('SELECT current_spent FROM budgets WHERE id = ?', (budget_id,))
        current_spent = self.cursor.fetchone()['current_spent']
        self.assertEqual(current_spent, 500.00)

    def test_update_nonexistent_budget(self):
        """Test updating a budget that doesn't exist"""
        with self.assertRaises(ValueError):
            update_budget(999, budget_name="Nonexistent Budget")

    def test_get_budgets_for_contact(self):
        """Test fetching budgets for a contact"""
        # Create test budgets
        self.cursor.executemany('''
            INSERT INTO budgets (contact_id, budget_name, total_budget, start_date, end_date, currency)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [
            (self.test_contact_id, 'Budget 1', 1000.00, '2025-01-01', '2025-12-31', 'USD'),
            (self.test_contact_id, 'Budget 2', 2000.00, '2025-01-01', '2025-12-31', 'EUR')
        ])
        self.conn.commit()
        
        budgets = get_budgets_for_contact(self.test_contact_id)
        self.assertEqual(len(budgets), 2)
        self.assertEqual(budgets[0]['budget_name'], 'Budget 1')
        self.assertEqual(budgets[1]['budget_name'], 'Budget 2')

    def test_get_budgets_for_nonexistent_contact(self):
        """Test fetching budgets for a contact that doesn't exist"""
        budgets = get_budgets_for_contact(999)
        self.assertEqual(len(budgets), 0)

    def test_delete_budget(self):
        """Test budget deletion"""
        # Create a budget to delete
        self.cursor.execute('''
            INSERT INTO budgets (contact_id, budget_name, total_budget, start_date, end_date, currency)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.test_contact_id, 'Budget to Delete', 1000.00, '2025-01-01', '2025-12-31', 'USD'))
        budget_id = self.cursor.lastrowid
        self.conn.commit()
        
        # Delete the budget
        delete_budget(budget_id)
        
        # Verify deletion
        self.cursor.execute('SELECT * FROM budgets WHERE id = ?', (budget_id,))
        budget = self.cursor.fetchone()
        self.assertIsNone(budget)

    def test_delete_nonexistent_budget(self):
        """Test deleting a budget that doesn't exist"""
        with self.assertRaises(ValueError):
            delete_budget(999)

    def test_create_multiple_budgets_same_contact(self):
        """Test creating multiple budgets for the same contact"""
        budget_data = [
            ("Budget 1", 1000.00, date(2025, 1, 1), date(2025, 6, 30), "USD"),
            ("Budget 2", 2000.00, date(2025, 7, 1), date(2025, 12, 31), "EUR"),
            ("Budget 3", 3000.00, date(2026, 1, 1), date(2026, 12, 31), "GBP")
        ]
        
        for name, amount, start, end, currency in budget_data:
            create_budget(self.test_contact_id, name, amount, start, end, currency)
        
        budgets = get_budgets_for_contact(self.test_contact_id)
        self.assertEqual(len(budgets), 3)
        
        # Verify each budget
        for i, budget in enumerate(budgets):
            self.assertEqual(budget['budget_name'], f"Budget {i+1}")
            self.assertEqual(budget['total_budget'], (i+1) * 1000.00)

    def test_budget_overspend_update(self):
        """Test updating budget with spent amount exceeding total budget"""
        self.cursor.execute('''
            INSERT INTO budgets (contact_id, budget_name, total_budget, current_spent, start_date, end_date, currency)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (self.test_contact_id, 'Overspend Budget', 1000.00, 0.00, '2025-01-01', '2025-12-31', 'USD'))
        budget_id = self.cursor.lastrowid
        self.conn.commit()
        
        with self.assertRaises(ValueError):
            update_budget(budget_id, current_spent=2000.00)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    unittest.main(verbosity=2)