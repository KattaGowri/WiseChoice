import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
back_folder_path = os.path.join(current_dir, '..')
sys.path.append(back_folder_path)

from BACKEND_FILES.Review_Extraction import Review_Extract
from BACKEND_FILES.Fake_Review_Detector import Fake_Review_Analysis
from BACKEND_FILES.Sentiment_Analysis import Sentiment_Analysis


import streamlit as st
from time import sleep
import pickle,csv,string,re,nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import pandas as pd
import plotly.graph_objs as go
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from joblib import load
# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')

def text_process(review):
    nopunc = [char for char in review if char not in string.punctuation]
    nopunc = ''.join(nopunc)
    return [word for word in nopunc.split() if word.lower() not in stopwords.words('english')]

custom_text_css = """
    <style>
        .custom-text {
            color: #ffffff;
        }
    </style>
"""



review_extracter = Review_Extract()
sentiment_analysis = Sentiment_Analysis("cardiffnlp/twitter-roberta-base-sentiment")
fake_review_filter = Fake_Review_Analysis()

with open('user.txt') as f:
    st.markdown(custom_text_css, unsafe_allow_html=True)
    st.header('Welcome '+f.read()+'!!!')
st.markdown(custom_text_css, unsafe_allow_html=True)   
link = st.text_input("Amazon/Flipkart Product Link",placeholder='Enter Product Link here')
col = st.columns(5)
with col[4]:
    b = st.button('Analyze')
if b:
    with st.spinner('Please wait..'):
        sleep(3)
    with st.status("Analyzing Product ....",expanded=True):
        #Review_Extraction
        st.write("Extracting Reviews....")
        review_extracter.launch()
        reviews = review_extracter.start(link)
        if reviews.empty:
            st.error("Product Doesnot have any Reviews")
        else:
            #Price Analysis
            st.write("Performing Price Analysis ...")
            status = review_extracter.price_cal(link)
            #Fake Review Detection
            st.write("Filtering out Fake Reviews ...")
            geniune_reviews = fake_review_filter.filter(reviews)
            #Sentiment Analysis
            st.write("Analyzing Sentiment ...")
            outs = list(sentiment_analysis.start(geniune_reviews))
            st.write(outs[0])
            st.plotly_chart(outs[1],use_container_width=True)
            st.write(outs[2])
            st.pyplot(outs[3],use_container_width=True)
            st.dataframe(outs[4],use_container_width=True)
            if status:
                st.write("Lowest Price   : "+str(review_extracter.prices['Lowest']))
                st.write("Highest Price  : "+str(review_extracter.prices['Highest']))
                st.write("Average Price  : "+str(review_extracter.prices['Average']))
                st.write("Price Fairness : "+str(review_extracter.fairness))
            else:
                st.write("Price Analysis Not Possible or Failed")
                
        review_extracter.finish()
        
        
