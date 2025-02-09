import streamlit as st
import sqlite3
from fpdf import FPDF
import base64
from io import BytesIO
from sqlite3 import Error
from datetime import datetime

# Function to connect to the database
def get_db_connection():
    try:
        conn = sqlite3.connect('crm.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

# Function to fetch contact and application details together
def fetch_contact_with_application(contact_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to join contact data with application data
    cursor.execute('''
        SELECT c.id, c.name, c.email, c.phone, a.interest, a.reason, a.skillsets, d.document_name
        FROM contacts c
        JOIN applications a ON c.id = a.contact_id
        LEFT JOIN application_documents d ON c.id = d.contact_id
        WHERE c.id = ?
    ''', (contact_id,))
    contact_data = cursor.fetchone()
    conn.close()

    # Check if contact data is found
    if contact_data:
        return {
            "id": contact_data["id"],
            "name": contact_data["name"],
            "email": contact_data["email"],
            "phone": contact_data["phone"],
            "interest": contact_data["interest"],
            "reason": contact_data["reason"],
            "skillsets": contact_data["skillsets"],
            "document_name": contact_data["document_name"]
        }
    return None

# Function to create a document in a blue professional format
def create_document(contact_name, contact_email, contact_phone, document_name, interest, reason, skillsets):
    pdf = FPDF()
    pdf.add_page()

    # Set title and header
    pdf.set_font("Arial", size=18, style='B')
    pdf.set_text_color(52, 152, 219)  # Blue color for the header
    pdf.cell(200, 10, txt="Application Form - Document", ln=True, align='C')
    pdf.ln(10)

    # Add contact info header
    pdf.set_font("Arial", size=14, style='B')
    pdf.cell(200, 10, txt="Contact Information", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)  # Black text
    pdf.cell(200, 10, txt=f"Name: {contact_name}", ln=True)
    pdf.cell(200, 10, txt=f"Email: {contact_email}", ln=True)
    pdf.cell(200, 10, txt=f"Phone: {contact_phone}", ln=True)
    pdf.ln(10)

    # Add application info header
    pdf.set_font("Arial", size=14, style='B')
    pdf.cell(200, 10, txt="Application Information", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Interest: {interest}", ln=True)
    pdf.cell(200, 10, txt=f"Reason: {reason}", ln=True)
    pdf.multi_cell(200, 10, txt=f"Skillsets: {skillsets}")
    pdf.ln(10)

    # Add document info
    pdf.set_font("Arial", size=14, style='B')
    pdf.cell(200, 10, txt="Document Information", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Document: {document_name}", ln=True)
    pdf.ln(10)

    # Signature section
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Signature: ____________________________________", ln=True)
    pdf.ln(10)

    # Timestamp at the bottom of the document
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(200, 10, txt=f"Document generated on: {timestamp}", ln=True)
    pdf.ln(20)

    # Create a buffer to store the PDF
    pdf_output = BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin1'))  # Write to memory buffer
    pdf_output.seek(0)  # Reset the buffer pointer to the beginning of the file

    return pdf_output

# Function to provide the PDF download link
def generate_and_download_pdf(contact_name, contact_email, contact_phone, document_name, interest, reason, skillsets):
    # Create the document
    pdf_output = create_document(contact_name, contact_email, contact_phone, document_name, interest, reason, skillsets)

    # Provide PDF download link
    pdf_output.seek(0)
    b64_pdf = base64.b64encode(pdf_output.read()).decode('utf-8')
    href = f'<a href="data:file/pdf;base64,{b64_pdf}" download="{document_name}.pdf">Download the document</a>'
    st.markdown(href, unsafe_allow_html=True)

# Streamlit interface
def document_page():
    st.title("Document Generation")

    # Fetch contacts and display the dropdown menu
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts")
    contacts = cursor.fetchall()
    conn.close()

    # Display a dropdown menu with the list of contacts
    if contacts:
        contact_names = [f"{contact['name']} ({contact['email']})" for contact in contacts]
        contact_selection = st.selectbox("Select a contact", contact_names)

        # Fetch selected contact details
        selected_contact = contacts[contact_names.index(contact_selection)]
        contact_id = selected_contact['id']

        # Fetch the contact and application details together
        contact_data = fetch_contact_with_application(contact_id)

        if contact_data:
            contact_name = contact_data["name"]
            contact_email = contact_data["email"]
            contact_phone = contact_data["phone"]
            interest = contact_data["interest"]
            reason = contact_data["reason"]
            skillsets = contact_data["skillsets"]
            document_name = contact_data["document_name"]

            # Display the contact information
            st.write(f"Contact ID: {contact_id}")
            st.write(f"Contact Name: {contact_name}")
            st.write(f"Contact Email: {contact_email}")
            st.write(f"Contact Phone: {contact_phone}")
            st.write(f"Interest: {interest}")
            st.write(f"Reason: {reason}")
            st.write(f"Skillsets: {skillsets}")

            # Button to generate and download PDF
            if st.button("Generate and Download Document"):
                generate_and_download_pdf(contact_name, contact_email, contact_phone, document_name, interest, reason, skillsets)
        else:
            st.write("No data found for this contact.")
    else:
        st.write("No contacts found in the database.")

# Run the document generation page
if __name__ == "__main__":
    document_page()