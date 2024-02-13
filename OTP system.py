import smtplib
from random import randint

otp = randint(100000,999999)
msg = "Your OTP is "+str(otp)

server = smtplib.SMTP("smtp.gmail.com",587)
server.starttls()
server.login('wisechoice953@gmail.com','gujaapcrtsyycnou')
server.sendmail('wisechoice953@gmail.com','kvkr0104@gmail.com',msg)

if otp == int(input("Enter The otp sent : ")):
    print("Thank you")
else:
    print("AASA DOSA APPADAM VADA")