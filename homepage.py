import streamlit as st

# Homepage layout design using Streamlit with white text and no box
def home():
    # Set the page config to make the homepage look modern
    st.set_page_config(page_title="CRM - Home", page_icon=":house:", layout="wide")

    # Add custom styles with CSS for white text and no box
    st.markdown("""
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f4f4f4; /* Lighter grey background */
                color: white; /* White text for better contrast */
                margin: 0;
                padding: 0;
            }

            .header {
                font-size: 50px;
                font-weight: 600;
                color: #3498db;
                text-align: center;
                margin-top: 50px;
                animation: fadeIn 1.5s ease-in-out;
            }

            .subtitle {
                font-size: 30px;
                color: white;
                text-align: center;
                margin-top: 10px;
                margin-bottom: 30px;
                animation: fadeIn 1.5s ease-in-out;
            }

            .content {
                font-size: 18px;
                color: white; /* White text */
                text-align: center;
                margin-bottom: 50px;
                animation: fadeIn 2s ease-in-out;
            }

            .box {
                padding: 20px;
                margin-top: 20px;
                animation: fadeIn 2s ease-in-out;
                text-align: center; /* Center the text */
                background-color: transparent; /* Remove the white box */
                border: none; /* Remove border */
            }

            .box p {
                margin-bottom: 20px;
            }

            .button {
                font-size: 18px;
                font-weight: bold;
                background-color: #3498db;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                border-radius: 12px;
                border: none;
                cursor: pointer;
                animation: bounceIn 1s ease-in-out;
            }

            .button:hover {
                background-color: #2980b9;
                transform: scale(1.1);
                transition: all 0.3s ease-in-out;
            }

            @keyframes fadeIn {
                0% {
                    opacity: 0;
                    transform: translateY(-20px);
                }
                100% {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            @keyframes bounceIn {
                0% {
                    opacity: 0;
                    transform: scale(0.5);
                }
                60% {
                    opacity: 1;
                    transform: scale(1.1);
                }
                100% {
                    transform: scale(1);
                }
            }
        </style>
    """, unsafe_allow_html=True)

    # Header section
    st.markdown('<div class="header">Welcome to Your CRM</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Efficient Contact Management System</div>', unsafe_allow_html=True)

    # Description of the CRM features with subtle animation
    st.markdown("""
        <div class="content">
            Welcome to the CRM system, designed to simplify the process of managing and interacting with your contacts. This platform allows you to:
        </div>
    """, unsafe_allow_html=True)

    # Box for the description without bullet points, text centered
    st.markdown("""
        <div class="box">
            <p>Add, update, and delete contacts</p>
            <p>Search contacts by name</p>
            <p>Send personalized emails to clients</p>
            <p>Maintain and organize customer data for better service</p>
        </div>
    """, unsafe_allow_html=True)

    # Call to Action button with animation
    st.markdown(""" 
        <div style="text-align:center;">
            <a href="http://localhost:8501/" class="button" style="color: white;">Manage Contacts</a>
        </div>
    """, unsafe_allow_html=True)

# Run the homepage function
if __name__ == "__main__":
    home()
