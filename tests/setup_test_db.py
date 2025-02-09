import sqlite3

def setup_test_database(db_path):
    """Initialize test database with required tables"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create contacts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            gender TEXT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            message TEXT,
            address_line TEXT,
            suburb TEXT,
            postcode TEXT,
            state TEXT,
            country TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create budgets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER,
            budget_name TEXT NOT NULL,
            total_budget REAL,
            current_spent REAL DEFAULT 0,
            start_date DATE,
            end_date DATE,
            currency TEXT DEFAULT 'USD',
            status TEXT DEFAULT 'active',
            FOREIGN KEY (contact_id) REFERENCES contacts (id)
        )
    ''')

    # Create budget_line_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budget_line_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            budget_id INTEGER,
            line_item_name TEXT NOT NULL,
            allocated_amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (budget_id) REFERENCES budgets (id)
        )
    ''')

    # Create applications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER,
            interest TEXT,
            reason TEXT,
            skillsets TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contact_id) REFERENCES contacts (id)
        )
    ''')

    conn.commit()
    return conn