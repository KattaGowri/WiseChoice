import streamlit as st
import DataBase_Manager
from os import system
from PIL import Image

conn = DataBase_Manager.DataBase()



st.markdown("<h1 style='color: #ffffff;'>WiseChoice</h1><h6 style='color: #ffffff;'>Your intelligent shopping companion</h6>", unsafe_allow_html=True)

st.markdown(
    """
    <style>
        %s
    </style>
    """
    % open("bgrnd.css").read(),
    unsafe_allow_html=True
)

custom_text_css = """
    <style>
        .custom-text {
            color: #ffffff;
        }
    </style>
"""

# Initialize session state
if 'username' not in st.session_state:
    st.session_state.username = None


col = st.columns(2)
st.session_state.username = None
with col[0]:
    st.header("Login")

# Input fields
with col[0]:
    st.markdown(custom_text_css, unsafe_allow_html=True)
    id = st.text_input("UserID", placeholder="Enter your Email-ID")
    pswrd = st.text_input("Password", type="password", placeholder="Enter your Password")
with col[1]:
    for i in range(18):
        st.write("")
    st.markdown(custom_text_css, unsafe_allow_html=True)
    if st.button('Login'):
        user = conn.login(id, pswrd)
        if user == -1:
            st.error("Incorrect Password!!!")
        elif user == -2:
            st.error("Invalid UserId!!!")
        else:
            st.success("Welcome " + user + "!!!")
            st.balloons()
            try:
                system('''for /f "tokens=5" %i in ('netstat -aon ^| find ":8503" ^| find "LISTENING"') do taskkill /F /PID %i''')
            except:
                pass
#                 st.session_state.username = user  # Store username in session state
            
            # Define HTML content with meta tag for redirection
            redirect_html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="refresh" content="0; URL='http://localhost:8503'" />
                <title>Redirecting...</title>
            </head>
            <body>
                <p>If you are not redirected automatically, <a href='http://localhost:8503'>click here</a>.</p>
            </body>
            </html>
            """

            # Render HTML content
            st.markdown(redirect_html, unsafe_allow_html=True)

            system('streamlit run WiseChoice.py --server.port 8503 --server.headless true '+user)
    redirect_html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
            </head>
            <body>
                <p>Don't have an account ? ?, <a href='http://localhost:8501'>Sign Up</a>.</p>
            </body>
            </html>
            """

            # Render HTML content
    st.markdown(redirect_html, unsafe_allow_html=True)
                
                