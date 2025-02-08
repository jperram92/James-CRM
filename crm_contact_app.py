import streamlit as st
import sqlite3
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('C:/Users/james/OneDrive/Desktop/James CRM/crm.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to insert a new contact
def insert_contact(title, gender, name, email, phone, message, address_line, suburb, postcode, state, country):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO contacts (title, gender, name, email, phone, message, address_line, suburb, postcode, state, country)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, gender, name, email, phone, message, address_line, suburb, postcode, state, country))  # 11 values
    conn.commit()
    conn.close()

# Function to update an existing contact by ID
def update_contact(contact_id, title, gender, name, email, phone, message, address_line, suburb, postcode, state, country):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE contacts
    SET title = ?, gender = ?, name = ?, email = ?, phone = ?, message = ?, address_line = ?, suburb = ?, postcode = ?, state = ?, country = ?
    WHERE id = ?
    ''', (title, gender, name, email, phone, message, address_line, suburb, postcode, state, country, contact_id))
    conn.commit()
    conn.close()

# Function to delete a contact by ID
def delete_contact(contact_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
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

# Function to send email using SMTP
def send_email(to_email, subject, body):
    from_email = "8542f6001@smtp-brevo.com"  # Replace with your email
    password = ""

    # Set up the MIME
    message = MIMEMultipart()
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = subject

    # Attach the body with the msg instance
    message.attach(MIMEText(body, 'plain'))

    # Establish a secure session with Gmail's SMTP server
    try:
        server = smtplib.SMTP('smtp-relay.brevo.com', 587)  # For Gmail
        server.starttls()  # Secure connection
        server.login(from_email, password)  # Log in to your email
        text = message.as_string()  # Convert the message to string
        server.sendmail(from_email, to_email, text)  # Send the email
        server.quit()  # Close the connection
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# Streamlit interface
st.title('Contact Management CRM')

# Create the right-hand email module in a sidebar
with st.sidebar:
    st.header("Email Client")
    
    # Email form fields
    to_email = st.text_input("To (Email Address)")
    subject = st.text_input("Subject")
    body = st.text_area("Body")

    send_button = st.button("Send Email")

    # Handle the Send button click
    if send_button and to_email and subject and body:
        if send_email(to_email, subject, body):
            st.success("Email sent successfully!")
        else:
            st.error("Failed to send email. Please check your credentials.")

# Get the contacts and convert them to a dataframe for display
contacts = display_contacts()
if contacts:
    # Convert the list of contacts into a DataFrame
    contacts_df = pd.DataFrame(contacts, columns=['id', 'title', 'gender', 'name', 'email', 'phone', 'message', 'address_line', 'suburb', 'postcode', 'state', 'country'])
    
    # Display the DataFrame as a table
    st.subheader('Existing Contacts')
    st.dataframe(contacts_df)  # This will display the contacts in a table format with custom size
else:
    st.write("No contacts available.")

# Contact form to add a new contact
st.subheader('Add New Contact')
with st.form(key='contact_form'):
    title = st.text_input("Title")
    gender = st.text_input("Gender")
    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    message = st.text_area("Message")
    address_line = st.text_input("Address Line")
    suburb = st.text_input("Suburb")
    postcode = st.text_input("Postcode")
    state = st.text_input("State")
    country = st.text_input("Country")
    
    submit_button = st.form_submit_button(label="Add Contact")
    
    if submit_button and title and gender and name and email and phone and message and address_line and suburb and postcode and state and country:
        insert_contact(title, gender, name, email, phone, message, address_line, suburb, postcode, state, country)
        st.success("Contact added successfully!")
        st.rerun()  # Refresh the app to show the new contact

# Search for existing contacts to update
st.subheader('Search for Contact to Update')
search_name = st.text_input("Enter the contact name to search for")

if search_name:
    search_results = search_contact_by_name(search_name)
    if search_results:
        for contact in search_results:
            st.write(f"ID: {contact['id']}, Name: {contact['name']}, Email: {contact['email']}, Phone: {contact['phone']}, Message: {contact['message']}, Address: {contact['address_line']}, Suburb: {contact['suburb']}, Postcode: {contact['postcode']}, State: {contact['state']}, Country: {contact['country']}")
            
            # Form to update a contact
            with st.form(key=f'update_form_{contact["id"]}'):
                update_title = st.text_input("Update Title", value=contact['title'])
                update_gender = st.text_input("Update Gender", value=contact['gender'])
                update_name = st.text_input("Update Name", value=contact['name'])
                update_email = st.text_input("Update Email", value=contact['email'])
                update_phone = st.text_input("Update Phone", value=contact['phone'])
                update_message = st.text_area("Update Message", value=contact['message'])
                update_address_line = st.text_input("Update Address Line", value=contact['address_line'])
                update_suburb = st.text_input("Update Suburb", value=contact['suburb'])
                update_postcode = st.text_input("Update Postcode", value=contact['postcode'])
                update_state = st.text_input("Update State", value=contact['state'])
                update_country = st.text_input("Update Country", value=contact['country'])
                
                update_button = st.form_submit_button(label="Update Contact")
                
                if update_button and update_title and update_gender and update_name and update_email and update_phone and update_message and update_address_line and update_suburb and update_postcode and update_state and update_country:
                    update_contact(contact['id'], update_title, update_gender, update_name, update_email, update_phone, update_message, update_address_line, update_suburb, update_postcode, update_state, update_country)  # Use ID for updating
                    st.success(f"Contact '{contact['name']}' updated successfully!")
                    st.rerun()  # Refresh the app to show the updated contact
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
            
            # Give each delete button a unique key based on the contact's ID
            delete_button = st.button(f"Delete {contact['name']}", key=f"delete_{contact['id']}")
            
            if delete_button:
                delete_contact(contact['id'])  # Use ID for deletion
                st.success(f"Contact '{contact['name']}' deleted successfully!")
                st.rerun()  # Refresh the app to remove the deleted contact
    else:
        st.warning(f"No contact found with the name '{delete_name}'.")
