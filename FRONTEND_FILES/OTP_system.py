import smtplib
from random import randint
import re

class OTP_SENDER:
    def opt_generate(self):
        return randint(100000,999999)
        
    def check(self,reciver):
        valid_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(valid_pattern, reciver) != None
    
    def send_mail(self,reciver):
        if self.check(reciver):
            otp = self.opt_generate()
            msg = """ Thanks for Signing Up to WiseChoice!!!
                        Your OTP for Verification is  """+str(otp)+'.'
            server = smtplib.SMTP("smtp.gmail.com",587)
            server.starttls()
            server.login('wisechoice953@gmail.com','gujaapcrtsyycnou')
            server.sendmail('wisechoice953@gmail.com',reciver,msg)
            print(otp)
            return otp
        else:
            return -1
        
if __name__=='__main__':
    obj = OTP_SENDER()
    print(obj.send_mail('@gmail.com'))