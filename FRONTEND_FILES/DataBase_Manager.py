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
            # Change username and password
            self.conn = mysql.connector.connect(host='localhost',database = "Login_Data",user = "WiseChoice",password = 'wisechoice@1')
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