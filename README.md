# WiseChoice
WiseChoice - Your Intelligent Shopping Companion:

This website will take a amazon or flipkart product link from you and it extracts the product reviews.
It will filter out Fake reviews using a ML model that has been trained with more than 3,00,00 reviews.
Then it will perform Sentiment Analysis on the Geniune Reviews and gives an overall rating.
All other language reviews will be translated into english by using google translate API

Download FakeReview model from this link and Save it in FRONTEND_FILES Folder :- 
      
      https://drive.google.com/drive/folders/1QTOahzhYT4-gzrlS3K0_a45LQ3c-XQZc?usp=sharing

Make sure you have MySql downloaded. open sql terminal prompt or workbench and execute the following queries :-

      create database Login_Data;
      use Login_Data;
      create table data(name varchar(30),email varchar(30),password varchar(50),PRIMARY KEY(name,email));
      commit;

Keep username as 'WiseChoice' and password as 'wisechoice@1'. Otherwise you have to change the username and password in the DataBase_Manager.py file.

Download all the modules mentioned in requirements.txt file. Use the following command:-
      
      pip install -r requirements.txt

Save every file including the models and chromedriver in the same directory. You also need to have google chrome installed. If you install the latest version of selenium, you wont be needing chromedriver.exe

After completing everything, open terminal and locate and move into that directory where you cloned the repository and run the below command :

      streamlit run login_signup.py

or just run the launch.py file to launch the application in browser.
