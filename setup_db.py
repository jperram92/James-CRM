import sqlite3

# Create a connection to the SQLite database (it will create the file if it doesn't exist)
conn = sqlite3.connect('crm.db')

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Create a table for storing contact information if it doesn't already exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    message TEXT NOT NULL
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and table created successfully!")
