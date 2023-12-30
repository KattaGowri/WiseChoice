# WiseChoice
WiseChoice - Your Intelligent Shopping Companion:

This website will take a amazon product link from you and it extracts the product reviews.
It will filter out Fake reviews using a ML model that has been trained with more than 3,00,00 reviews.
Then it will perform Sentiment Analysis on the Geniune Reviews and gives an overall rating.
All other language reviews will be translated into english by using google translate API

download FakeReview model and Sentiment Analysis model from this link :- https://drive.google.com/file/d/1ThHsQBTylBRPO6ZBlJv0D4HjyPXFJYWe/view?usp=sharing

Make sure you have MySql downloaded. open sql terminal prompt or workbench and execute the following queries :-
create database Login_Data;
use Login_Data;
create table data(name varchar(30),email varchar(30),password varchar(50),PRIMARY KEY(name,email));
commit;

You have to change the username, Password in the DataBase_Manager.py file

Download all the modules mentioned in modules.txt file
Save every file including the models in the same directory

After completing everything, open terminal and loacte and move into that directory and run the below command :
      streamlit run login_signup.py
