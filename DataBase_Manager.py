import mysql.connector
from random import randint
def encode(s,d=randint(10,78)):
    c=''
    for i in s:
        ord_v=ord(i)
        c_v=ord_v+d
        c=c+chr(c_v)
    l=list(str(d))
    return l[1]+c+l[0]

def decode(c):
    d=int(c[-1]+c[0])
    s=''
    for i in c:
        if not i.isnumeric():
            ord_v=ord(i)
            c_v=ord_v-d
            s=s+chr(c_v)
    return s

class DataBase:
    def __init__(self):
        try:
            #Change username and password arguments to your username and password
            self.conn = mysql.connector.connect(host='localhost',database = "Login_Data",user = "WiseChoice",password = 'HinokamiKagura',auth_plugin='mysql_native_password')
            self.cur = self.conn.cursor()
        except :
            pass
        
        
    def check(self,email,name=None):
        self.fetch()
        access = email in self.data.keys()
        if name == None :
            return access
        return access or name in [i[0] for i in self.data.values()]
        
        
        
    def enter(self,name,email,password):
        if not self.check(email,name):
            self.cur.execute("Insert into DATA values('"+name+"','"+email+"','"+encode(password)+"')")
            self.conn.commit()
            return True
        else:
            return False 
        
    def fetch(self):
        self.cur.execute('Select * from data')
        self.data = {}
        for i in self.cur.fetchall():
            self.data[i[1]] = [i[0],i[2]]
        
    def login(self,id,password):
        if self.check(id):
            if password == decode(self.data[id][1]):
                return self.data[id][0]
            else:
                return -1
        else:
            return -2
    
    def finish(self):
        self.cur.close()
        self.conn.close()
DataBase()
# import streamlit as st
# 
# 
# conn = DataBase()
# 
# st.markdown("<h1 style='color: #3366cc;'>WiseChoice</h1><h5 style='color: #3366cc;'>Your intelligent shopping companion</h5>", unsafe_allow_html=True)
# 
# 
# st.markdown(
#     """
#     <style>
#         %s
#     </style>
#     """
#     % open("bgrnd.css").read(),
#     unsafe_allow_html=True
# )
# 
# 
# 
# # Sidebar navigation
# page = st.sidebar.radio("Select a page", ["Login", "Signup"])
# col = st.columns(2)
# 
# if page == "Login":
#     with col[0]:
#         st.header("Login")
# 
#     # Input fields
#     with col[0]:
#         id = st.text_input("Username")
#         pswrd = st.text_input("Password", type="password")
#     with col[1]:
#         for i in range(23):
#             st.write("")
#         b = st.button('login')
#     if b:
#         user = conn.login(id,pswrd)
#         if user==-1:
#             st.error("Incorrect Password!!!")
#         elif user == -2:
#             st.error("Invalid UserId!!!")
#         else:
#             st.info("Welcome "+user+"!!!")
#             
#     
#     
# elif page == "Signup":
#     with col[0]:
#         st.header("Signup")
#         signup_username = st.text_input("Choose a username")
#         signup_mailid = st.text_input('Mail Id')
#         signup_password = st.text_input("Choose a password", type="password")
#     with col[1]:
#         for i in range(28):
#             st.write("")
#         st.button('signup')
