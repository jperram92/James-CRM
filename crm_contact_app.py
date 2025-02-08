import streamlit as st
import sqlite3

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('C:/Users/james/OneDrive/Desktop/James CRM/crm.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to insert a new contact
def insert_contact(name, email, phone, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO contacts (name, email, phone, message) 
    VALUES (?, ?, ?, ?)
    ''', (name, email, phone, message))
    conn.commit()
    conn.close()

# Function to update an existing contact
def update_contact(contact_name, name, email, phone, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE contacts
    SET name = ?, email = ?, phone = ?, message = ?
    WHERE name = ?
    ''', (name, email, phone, message, contact_name))
    conn.commit()
    conn.close()

# Function to delete a contact
def delete_contact(contact_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM contacts WHERE name = ?', (contact_name,))
    conn.commit()
    conn.close()

# Function to search for contacts by name
def search_contact_by_name(search_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts WHERE name LIKE ?', ('%' + search_name + '%',))
    contacts = cursor.fetchall()
    conn.close()
    return contacts

# Function to display contacts
def display_contacts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts')
    contacts = cursor.fetchall()
    conn.close()
    return contacts

# Streamlit interface
st.title('Contact Management CRM')

# Display existing contacts
contacts = display_contacts()
if contacts:
    st.subheader('Existing Contacts')
    for contact in contacts:
        st.write(f"ID: {contact['id']}, Name: {contact['name']}, Email: {contact['email']}, Phone: {contact['phone']}, Message: {contact['message']}")

# Contact form to add a new contact
st.subheader('Add New Contact')
with st.form(key='contact_form'):
    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    message = st.text_area("Message")
    
    submit_button = st.form_submit_button(label="Add Contact")
    
    if submit_button and name and email and phone and message:
        insert_contact(name, email, phone, message)
        st.success("Contact added successfully!")

# Search for existing contacts to update
st.subheader('Search for Contact to Update')
search_name = st.text_input("Enter the contact name to search for")

if search_name:
    search_results = search_contact_by_name(search_name)
    if search_results:
        for contact in search_results:
            st.write(f"ID: {contact['id']}, Name: {contact['name']}, Email: {contact['email']}, Phone: {contact['phone']}, Message: {contact['message']}")
            
            # Form to update a contact
            with st.form(key=f'update_form_{contact["id"]}'):
                update_name = st.text_input("Update Name", value=contact['name'])
                update_email = st.text_input("Update Email", value=contact['email'])
                update_phone = st.text_input("Update Phone", value=contact['phone'])
                update_message = st.text_area("Update Message", value=contact['message'])
                
                update_button = st.form_submit_button(label="Update Contact")
                
                if update_button and update_name and update_email and update_phone and update_message:
                    update_contact(contact['name'], update_name, update_email, update_phone, update_message)
                    st.success(f"Contact '{contact['name']}' updated successfully!")
    else:
        st.warning(f"No contact found with the name '{search_name}'.")

# Search for existing contacts to delete
st.subheader('Search for Contact to Delete')
delete_name = st.text_input("Enter the contact name to delete")

if delete_name:
    search_results_to_delete = search_contact_by_name(delete_name)
    if search_results_to_delete:
        for contact in search_results_to_delete:
            st.write(f"ID: {contact['id']}, Name: {contact['name']}, Email: {contact['email']}, Phone: {contact['phone']}, Message: {contact['message']}")
            
            delete_button = st.button(f"Delete {contact['name']}")
            
            if delete_button:
                delete_contact(contact['name'])
                st.success(f"Contact '{contact['name']}' deleted successfully!")
    else:
        st.warning(f"No contact found with the name '{delete_name}'.")
