import streamlit as st
import sqlite3
from fpdf import FPDF
import base64
from io import BytesIO
from sqlite3 import Error  # Add this import for Error handling

# Function to connect to the database
def get_db_connection():
    try:
        conn = sqlite3.connect('crm.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

# Function to fetch contacts from the database
def fetch_contacts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts")
    contacts = cursor.fetchall()
    conn.close()
    return contacts

# Function to insert document data into the database
def insert_document(contact_id, document_name, document_path, signature):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(''' 
        INSERT INTO application_documents (contact_id, document_name, document_path, signature)
        VALUES (?, ?, ?, ?)
    ''', (contact_id, document_name, document_path, signature))
    conn.commit()
    conn.close()

# Function to create a document in a blue professional format
def create_document(contact_id, contact_name, contact_email, contact_phone):
    # Create PDF document with fpdf
    pdf = FPDF()
    pdf.add_page()

    # Set title and header
    pdf.set_font("Arial", size=16, style='B')
    pdf.set_text_color(52, 152, 219)  # Blue color for the header
    pdf.cell(200, 10, txt="Application Form - Signed Document", ln=True, align='C')

    # Add contact info
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)  # Black text
    pdf.cell(200, 10, txt=f"Contact Name: {contact_name}", ln=True)
    pdf.cell(200, 10, txt=f"Contact Email: {contact_email}", ln=True)
    pdf.cell(200, 10, txt=f"Contact Phone: {contact_phone}", ln=True)

    # Add document content
    pdf.ln(10)
    pdf.multi_cell(200, 10, txt="This is a generated document for application submission. Please review the content below and provide your signature in the designated area.")

    # Signature section
    pdf.ln(10)
    pdf.cell(200, 10, txt="Signature: ____________________________________")
    pdf.ln(20)

    # Create a buffer to store the PDF
    pdf_output = BytesIO()

    # Manually write to the buffer instead of using pdf.output(pdf_output)
    # Convert the PDF content into bytes and write to the buffer
    pdf_output.write(pdf.output(dest='S').encode('latin1'))  # 'S' writes the content to memory
    pdf_output.seek(0)  # Reset the buffer pointer to the beginning of the file

    return pdf_output

# Function to allow the user to sign the document
def capture_signature():
    st.subheader("Please sign the document below")
    signature = st.text_area("Type your signature:", "")
    
    if st.button("Submit Signature"):
        return signature
    return None

def generate_and_store_document(contact_id, contact_name, contact_email, contact_phone):
    # Trim any leading/trailing spaces from the input fields, but don't strip contact_id since it's an integer
    contact_name = contact_name.strip() if contact_name else ""
    contact_email = contact_email.strip() if contact_email else ""
    contact_phone = contact_phone.strip() if contact_phone else ""
    
    # Validate contact details - Check if any field is empty
    if not contact_name or not contact_email or not contact_phone:
        st.error("Please fill in all the contact details.")
        return
    
    # Generate the document
    pdf_output = create_document(contact_id, contact_name, contact_email, contact_phone)
    
    # Capture the signature
    signature = capture_signature()
    
    if signature:
        # Save the document with the signature
        document_name = f"application_form_{contact_id}.pdf"
        document_path = f"/path/to/store/{document_name}"
        
        # Insert the document data into the database
        insert_document(contact_id, document_name, document_path, signature)
        
        # Display success message
        st.success("Document generated and signature saved successfully!")

        # Show the signature for verification
        st.write(f"Captured Signature: {signature}")

        # Optionally, you can save the PDF to a file system
        with open(document_path, "wb") as f:
            f.write(pdf_output.read())
        
        # Return PDF for download
        pdf_output.seek(0)
        b64_pdf = base64.b64encode(pdf_output.read()).decode('utf-8')
        href = f'<a href="data:file/pdf;base64,{b64_pdf}" download="document.pdf">Download the document</a>'
        st.markdown(href, unsafe_allow_html=True)

# Streamlit interface
def document_page():
    st.title("Document Generation and Signature")

    # Fetch contacts from the database
    contacts = fetch_contacts()

    # Display a dropdown menu with the list of contacts
    if contacts:
        contact_names = [f"{contact['name']} ({contact['email']})" for contact in contacts]
        contact_selection = st.selectbox("Select a contact", contact_names)

        # Fetch selected contact details
        selected_contact = contacts[contact_names.index(contact_selection)]
        contact_id = selected_contact['id']
        contact_name = selected_contact['name']
        contact_email = selected_contact['email']
        contact_phone = selected_contact['phone']

        # Display the contact information
        st.write(f"Contact ID: {contact_id}")
        st.write(f"Contact Name: {contact_name}")
        st.write(f"Contact Email: {contact_email}")
        st.write(f"Contact Phone: {contact_phone}")

        # Generate document button
        if st.button("Generate Document"):
            generate_and_store_document(contact_id, contact_name, contact_email, contact_phone)
    else:
        st.write("No contacts found in the database.")

# Run the document generation page
if __name__ == "__main__":
    document_page()
