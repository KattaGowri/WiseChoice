import streamlit as st
import DataBase_Manager
from os import system
from OTP_system import OTP_SENDER  # Import your OTP_SENDER class

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

# Sidebar navigation
page = st.sidebar.radio("Select a page", ["Login", "Signup"])
col = st.columns(2)
conn = DataBase_Manager.DataBase()
otp_sender = OTP_SENDER()  # Create an instance of OTP_SENDER class

if page == "Login":
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
                with open('user.txt', 'w') as f:
                    f.write(user)
                system('streamlit run link_page.py')

elif page == "Signup":
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
                st.session_state.session = {'generated_otp': generated_otp}  # Store generated_otp in session state
            else:
                st.error("Invalid email format. Please enter a valid email.")
        if st.button('Register'):
            if st.session_state.session is not None and st.session_state.session['generated_otp'] is not None:
                if str(st.session_state.session['generated_otp']) == otp:
                    if conn.enter(username, mailid, password):
                        st.success("Account Created Successfully")
                    else:
                        st.error("Account Already Exists")
                else:
                    st.error("Invalid OTP. Please enter the correct OTP.")
            else:
                st.error("Please generate OTP first.")

