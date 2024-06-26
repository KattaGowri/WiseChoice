import streamlit as st
import DataBase_Manager
from OTP_system import OTP_SENDER  # Import your OTP_SENDER class
from os import system
from PIL import Image

conn = DataBase_Manager.DataBase()
otp_sender = OTP_SENDER()


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
    
st.session_state.username = None
col = st.columns(2)

with col[0]:
    st.header("Signup")
    st.markdown(custom_text_css, unsafe_allow_html=True)
    username = st.text_input("Choose a username", placeholder="Create a UserName")
    mailid = st.text_input('Mail Id', placeholder="Enter your Email ID")
    password = st.text_input("Choose a password", type="password", placeholder="Create Your Password")
    otp = st.text_input("Enter OTP", placeholder="Enter OTP received via email")
with col[1]:
    for i in range(27):
        st.write("")
    if st.button('Send OTP'):
        generated_otp = otp_sender.send_mail(mailid)
        if generated_otp != -1:
            st.success("OTP sent successfully")
            st.session_state.generated_otp = generated_otp  # Store generated_otp in session state
        else:
            st.error("Invalid email format. Please enter a valid email.")
    if st.button('Register'):
        if st.session_state.generated_otp is not None:
            if str(st.session_state.generated_otp) == otp:
                if conn.enter(username, mailid, password):
                    st.success("Account Created Successfully")
                    redirect_html = """
                                    <!DOCTYPE html>
                                    <html lang="en">
                                    <head>
                                        <meta charset="UTF-8">
                                        <meta http-equiv="refresh" content="0; URL='http://localhost:8502'" />
                                        <title>Redirecting...</title>
                                    </head>
                                    <body>
                                        <p>If you are not redirected automatically, <a href='http://localhost:8502'>click here</a>.</p>
                                    </body>
                                    </html>
                                    """

                                    # Render HTML content
                    st.markdown(redirect_html, unsafe_allow_html=True)
                else:
                    st.error("Account Already Exists")
            else:
                st.error("Invalid OTP. Please enter the correct OTP.")
        else:
            st.error("Please generate OTP first.")
    redirect_html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
            </head>
            <body>
                <p>Already have a account ?, <a href='http://localhost:8502'>Login</a>.</p>
            </body>
            </html>
            """

            # Render HTML content
    st.markdown(redirect_html, unsafe_allow_html=True)
