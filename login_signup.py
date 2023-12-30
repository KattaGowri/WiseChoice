import streamlit as st
import DataBase_Manager
from os import system

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
if page == "Login":
    with col[0]:
        st.header("Login")

    # Input fields
    with col[0]:
        st.markdown(custom_text_css, unsafe_allow_html=True)
        id = st.text_input("UserID",placeholder="Enter your Email-ID")
        pswrd = st.text_input("Password", type="password",placeholder="Enter your Password")
    with col[1]:
        for i in range(18):
            st.write("")
        st.markdown(custom_text_css, unsafe_allow_html=True)
        if st.button('Login'):
            user = conn.login(id,pswrd)
            if user==-1:
                st.markdown(custom_text_css, unsafe_allow_html=True)
                st.error("Incorrect Password!!!")
            elif user == -2:
                st.markdown(custom_text_css, unsafe_allow_html=True)
                st.error("Invalid UserId!!!")
            else:
                st.markdown(custom_text_css, unsafe_allow_html=True)
                st.success("Welcome "+user+"!!!")
                st.balloons()
                with open('user.txt','w') as f:
                    f.write(user)
                system('streamlit run link_page.py')
                
            
    
    
elif page == "Signup":
    with col[0]:
        st.header("Signup")
        st.markdown(custom_text_css, unsafe_allow_html=True)
        username = st.text_input("Choose a username",placeholder="Create a UserName")
        mailid = st.text_input('Mail Id',placeholder="Enter your Email ID")
        password = st.text_input("Choose a password", type="password",placeholder="Create Your Password")
    with col[1]:
        for i in range(24):
            st.write("")
        if st.button('Register'):
            if conn.enter(username,mailid,password):
                st.markdown(custom_text_css, unsafe_allow_html=True)
                st.success("Account Created Successfully")
            else:
                st.markdown(custom_text_css, unsafe_allow_html=True)
                st.error("Account Already Exists")
            