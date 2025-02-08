import streamlit as st
import requests

# Homepage layout design using Streamlit
def home():
    # Customizing the page layout and theme
    st.set_page_config(page_title="CRM - Home", page_icon=":house:", layout="wide")

    # Add a custom header with styling
    st.markdown("""
        <style>
            .header {
                font-size: 50px;
                font-weight: 600;
                color: #4CAF50;
                text-align: center;
                margin-top: 20px;
            }
            .subtitle {
                font-size: 30px;
                color: #333;
                text-align: center;
                margin-top: 10px;
                margin-bottom: 30px;
            }
            .content {
                font-size: 18px;
                color: #555;
                text-align: center;
            }
            .button {
                font-size: 20px;
                font-weight: bold;
                background-color: #4CAF50;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                border-radius: 12px;
                border: none;
            }
            .button:hover {
                background-color: #45a049;
            }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<div class="header">Welcome to Your CRM</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Efficient Contact Management System</div>', unsafe_allow_html=True)

    # Description of the CRM
    st.markdown("""
        <div class="content">
            <p>Welcome to the CRM system, designed to simplify the process of managing and interacting with your contacts. This platform allows you to:</p>
            <ul style="list-style-type:square;">
                <li>Add, update, and delete contacts</li>
                <li>Search contacts by name</li>
                <li>Send personalized emails to clients</li>
                <li>Maintain and organize customer data for better service</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    # Call to Action button to navigate to the contact management page
    st.markdown("""
        <div style="text-align:center;">
            <a href="http://localhost:8501/" class="button">Manage Contacts</a>
        </div>
    """, unsafe_allow_html=True)

    # Optional: Add image or branding for a sleek look
    # st.image("path_to_image_or_logo.jpg", width=200)

# Run the homepage function
if __name__ == "__main__":
    home()
