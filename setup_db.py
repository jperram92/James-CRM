import sqlite3

# Create a connection to the SQLite database (it will create the file if it doesn't exist)
conn = sqlite3.connect('crm.db')

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Drop the tables if they exist (use with caution - this will delete data)
cursor.execute('DROP TABLE IF EXISTS contacts')
cursor.execute('DROP TABLE IF EXISTS applications')

# Create a table for storing contact information if it doesn't already exist
cursor.execute(''' 
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    gender TEXT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    message TEXT NOT NULL,
    address_line TEXT,
    suburb TEXT,
    postcode TEXT,
    state TEXT,
    country TEXT
)
''')

# Create a table for storing application data linked to contacts
cursor.execute(''' 
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER,
    interest TEXT NOT NULL,
    reason TEXT NOT NULL,
    skillsets TEXT NOT NULL,
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
)
''')

# Insert some sample (rubbish) data into the contacts table for testing
cursor.executemany('''
INSERT INTO contacts (title, gender, name, email, phone, message, address_line, suburb, postcode, state, country)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', [
    ('Mr.', 'Male', 'John Doe', 'john.doe@example.com', '1234567890', 'Interested in testing.', '123 Main St', 'Somewhere', '1234', 'NSW', 'Australia'),
    ('Ms.', 'Female', 'Jane Smith', 'jane.smith@example.com', '0987654321', 'Looking to apply.', '456 Elm St', 'Anywhere', '5678', 'VIC', 'Australia'),
    ('Dr.', 'Non-binary', 'Alex Taylor', 'alex.taylor@example.com', '1122334455', 'Testing with dummy data.', '789 Oak St', 'Nowhere', '9101', 'QLD', 'Australia'),
    ('Prof.', 'Male', 'William Brown', 'william.brown@example.com', '2233445566', 'Trying the system out.', '101 Pine St', 'Everywhere', '1122', 'SA', 'Australia'),
    ('Ms.', 'Female', 'Emily White', 'emily.white@example.com', '3344556677', 'Just exploring.', '202 Maple St', 'Anywhere', '3344', 'WA', 'Australia')
])

# Insert some sample (rubbish) data into the applications table for testing
cursor.executemany('''
INSERT INTO applications (contact_id, interest, reason, skillsets)
VALUES (?, ?, ?, ?)
''', [
    (1, 'Data Analyst', 'Interested in data processing and analysis.', 'Excel, Python, SQL'),
    (2, 'Web Developer', 'Want to build websites and web applications.', 'HTML, CSS, JavaScript'),
    (3, 'AI Researcher', 'Passionate about machine learning and AI technologies.', 'Python, TensorFlow, Keras'),
    (4, 'Project Manager', 'Looking to manage large-scale projects.', 'Leadership, Agile, Communication'),
    (5, 'Content Writer', 'Love creating content and articles for blogs and websites.', 'Writing, SEO, Research')
])

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database, tables, and test data created successfully!")
