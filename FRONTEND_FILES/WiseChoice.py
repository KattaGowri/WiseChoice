import sys
import os
import mysql.connector
current_dir = os.path.dirname(os.path.abspath(__file__))
back_folder_path = os.path.join(current_dir, '..')
sys.path.append(back_folder_path)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
from plotly import graph_objects as go
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from joblib import load
import bot
# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')

username =  sys.argv[1]
redirect_script = """
<script>
    // Function to redirect when sidebar back button is clicked
    document.addEventListener('DOMContentLoaded', function() {
        document.querySelector('.sidebar').addEventListener('click', function(event) {
            if (event.target.classList.contains('sidebar--back-button')) {
                window.location.href = 'https://www.google.com';
            }
        });
    });
</script>
"""

# Render the redirection script
st.markdown(redirect_script, unsafe_allow_html=True)

def search_and_extract_amazon(product_name):
    driver = webdriver.Chrome()
    driver.get("https://www.amazon.in/")
    search_bar = WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
    )

    search_bar.send_keys(product_name)

    search_bar.submit()

    # Wait for the search results page to load
    WebDriverWait(driver, 10).until(EC.title_contains("Amazon.in"))
    titles = []
    links = []
    sleep(5)
    pages = int(driver.find_element(By.XPATH,"//span[@class='s-pagination-item s-pagination-disabled']").text) - 1
    for i in range(pages):
      btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH,"//a[@class='s-pagination-item s-pagination-next s-pagination-button s-pagination-separator']")))
      titles.extend(list(map(lambda x:x.text,driver.find_elements(By.XPATH, "//h2[@class='a-size-mini a-spacing-none a-color-base s-line-clamp-2']//span[@class='a-size-medium a-color-base a-text-normal']"))))
      links.extend(list(map(lambda x:x.get_attribute('href'),driver.find_elements(By.XPATH, "//a[@class='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal']"))))
      btn.click()
      WebDriverWait(driver, 15).until(EC.title_contains("Amazon.in"))
    
    driver.quit()
    return links, titles
    
    
def search_and_extract_flipkart(prod):
    d = webdriver.Chrome()
    d.get('https://www.flipkart.com')
    sleep(2)
    ip = d.find_element(By.CLASS_NAME,'Pke_EE')
    ip.send_keys('AC')
    ip.submit()
    WebDriverWait(d, 15).until(EC.element_to_be_clickable((By.CLASS_NAME,'_9QVEpD'))).click()
    titls = []
    links = []
    pages = int(d.find_element(By.XPATH,"//div[@class='_1G0WLw']//span").text.split()[-1])

    l = d.current_url[:-1]
    for i in range(pages):
        if len(titls > 100):
            break
        d.get(f'{l}{i+1}')
        sleep(1)
        prods = d.find_elements(By.XPATH,"//div[@class='_75nlfW']")
        titls.extend(list(map(lambda x:x.find_element(By.CLASS_NAME,'KzDlHZ').text,prods)))
        links.extend(list(map(lambda x:x.find_element(By.CLASS_NAME,'CGtC98').get_attribute('href'),prods)))
    
    d.quit()
    return titls, links

    

    
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

# Parse arguments to get username
page = st.sidebar.radio('Select ',['Analyzer','Alerts','You Ask We Say'])

conn =''
if conn not in st.session_state:
    st.session_state.conn = mysql.connector.connect(host='localhost',database = "Login_Data",user = "WiseChoice",password = 'wisechoice@1')
    st.session_state.cur = st.session_state.conn.cursor()
    st.session_state.do = True

if page == 'Analyzer':
    st.session_state.do = True
    review_extracter = Review_Extract()
    sentiment_analysis = Sentiment_Analysis("cardiffnlp/twitter-roberta-base-sentiment")
    fake_review_filter = Fake_Review_Analysis()

    st.markdown(custom_text_css, unsafe_allow_html=True)
    st.header('Welcome '+ str(username) +'!!!')  # Use username passed as an argument

    st.markdown(custom_text_css, unsafe_allow_html=True)   
    link = st.text_input("Amazon/Flipkart/Myntra Product Link",placeholder='Enter Product Link here')
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
            try:
                reviews = review_extracter.start(link)
                pos = False
            except Exception as e:
                reviews = pd.DataFrame([])
                pos = True
            if pos:
                st.error('Unable to Extract Reviews')
            elif reviews.empty:
                st.error("Product Doesnot have any Reviews")
            else:
                #Price Analysis
                st.write("Performing Price Analysis ...")
                status,graph,context = review_extracter.price_cal(link)
                #Fake Review Detection
                st.write("Filtering out Bot Generated Fake Reviews ...")
                geniune_reviews = fake_review_filter.filter(reviews)
                st.write("Filtering out Human Generated Fake Reviews ...")
                sleep(5)
                #Sentiment Analysis
                st.write("Analyzing Sentiment ...")
                outs = list(sentiment_analysis.start(geniune_reviews))
                st.write(outs[0])
                st.plotly_chart(outs[1],use_container_width=True)
                st.write(outs[2])
                if outs[3] != '':
                    st.pyplot(outs[3],use_container_width=True)
                positive_weight = 1
                neutral_weight = 0.5
                negative_weight = -1
                positive, negative,neutral = outs[-1]
                weighted_sum = (positive * positive_weight) + (neutral * neutral_weight) + (negative * negative_weight)

                total_reviews = positive + neutral + negative
                try:
                    score = (weighted_sum / total_reviews) * 100
                except:
                    score  = 0
                st.markdown('<h4>Sentiment Score : </h4>', unsafe_allow_html=True)
                fig = go.Figure(go.Indicator(
                                          mode="gauge+number+delta",
                                          value=int(score),
                                          domain={'x': [0, 1], 'y': [0, 1]},
                                          gauge={
                                              'shape': 'angular',
                                              'axis': {'range': [0, 100]},  # Adjust gauge range here (0-100 for your score)
                                              'bar': {'color': "darkorange"},  # Customize gauge color
                                              'bgcolor': 'white',
                                              'borderwidth': 2,
                                              'bordercolor': 'gray'
                                          },
                                          title={'text': "Score"}
                                      ))
                fig.update_layout(margin=dict(t=40, b=40, l=40, r=40), width=500, height=300)
                st.plotly_chart(fig)
                st.dataframe(outs[4],use_container_width=True)
                if status:
                    st.markdown('<h4>Price Analysis : </h4>', unsafe_allow_html=True)
                    st.write('')
                    st.markdown(graph, unsafe_allow_html=True)
                    st.markdown('<h5>Future Forecast : </h4\5>', unsafe_allow_html=True)
                    st.write(context)
                    st.write("Current Price  : "+str(review_extracter.prices['Current']))
                    st.write("Lowest Price   : "+str(review_extracter.prices['Lowest']))
                    st.write("Highest Price  : "+str(review_extracter.prices['Highest']))
                    st.write("Average Price  : "+str(review_extracter.prices['Average']))
                    st.markdown('<h5>Price Fairness Score : </h5>', unsafe_allow_html=True)
                    fig = go.Figure(go.Indicator(
                                          mode="gauge+number+delta",
                                          value=review_extracter.fairness,
                                          domain={'x': [0, 1], 'y': [0, 1]},
                                          gauge={
                                              'shape': 'angular',
                                              'axis': {'range': [0, 100]},  # Adjust gauge range here (0-100 for your score)
                                              'bar': {'color': "darkorange"},  # Customize gauge color
                                              'bgcolor': 'white',
                                              'borderwidth': 2,
                                              'bordercolor': 'gray'
                                          },
                                          title={'text': "Score"}
                                      ))
                    fig.update_layout(margin=dict(t=40, b=40, l=40, r=40), width=500, height=300)
                    st.plotly_chart(fig)
                    st.write("Price Fairness : "+str(review_extracter.fairness))
                    
                else:
                    st.write("Price Analysis Not Possible or Failed")
                try:
                    data = ''
                    geniune_reviews.columns = ['Reviews']
                    for i in list(geniune_reviews['Reviews']):
                        data += i+'\n'
                    data = bot.process(data).replace('\n\n','\n').split('\n')
                    pros = data[1:6]
                    cons = data[7:]
                    pro = ''
                    for i in pros:
                        pro += i+'\n\n'
                    st.markdown(f'<h3>Pros : </h3>', unsafe_allow_html=True)
                    st.write(pro)
                    st.markdown(f'<h3>Cons : </h3>', unsafe_allow_html=True)
                    con = ''
                    for i in cons:
                        con += i +'\n\n'
                    st.write(con)
                    st.markdown('<h3>Final Report : </h3>',unsafe_allow_html=True)
                    grade=0.6*score+0.4*review_extracter.fairness
                    if grade<=20:
                        st.markdown('<div style="text-align: center;"><span style="font-size: 5em;">D</span></div>',unsafe_allow_html=True)
                    elif grade<=40:
                        st.markdown('<div style="text-align: center;"><span style="font-size: 5em;">C</span></div>',unsafe_allow_html=True)
                    elif grade<=60:
                        st.markdown('<div style="text-align: center;"><span style="font-size: 5em;">B</span></div>',unsafe_allow_html=True)
                    elif grade<=80:
                        st.markdown('<div style="text-align: center;"><span style="font-size: 5em;">A</span></div>',unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="text-align: center;"><span style="font-size: 5em;">S</span></div>',unsafe_allow_html=True)   
                except:
                    pass
                
                review_extracter.driver.get(link)
                p1 = review_extracter.driver.find_element(By.ID,'productTitle').text
                if 'amazon' in link:
                    review_extracter.driver.get('https://www.flipkart.com')
                    ip = review_extracter.driver.find_element(By.CLASS_NAME,'Pke_EE')
                    ip.send_keys(p1)
                    ip.submit()
                    p2s = review_extracter.driver.find_elements(By.CLASS_NAME,'KzDlHZ')[:5]
                    p2 = ''
                    p2s = list(map(lambda x:x.text,p2s))
                    for i in p2s:
                        if bot.product_comp(p1,i) == 'True':
                            p2 = i
                            break
                    if p2 == '':
                        pass
                    else:
                        prices = review_extracter.driver.find_elements(By.XPATH,"//div[@class='Nx9bqj _4b5DiR']")[:5]
                        prices = list(map(lambda x:float(x.text.replace(',','').replace('₹','')),prices))
                        if review_extracter.prices['Current'] > prices[p2s.index(p2)]:
                            st.write('Similar Product is available at a lower price at  Flipkart ')
                            link = review_extracter.driver.find_elements(By.CLASS_NAME,'CGtC98')[p2s.index(p2)].get_attribute('href')
                            st.markdown(f'<div style="text-align: center;"><span style="font-size: 3em;">{prices[p2s.index(p2)]}</span></div>',unsafe_allow_html=True)
                            st.markdown(f'<a href="{link}">Click to Follow </a>',unsafe_allow_html=True)                         
                            
                else:
                    pass
            review_extracter.finish()
            
    

if st.session_state.do and page == 'Alerts':
    st.session_state.do = False
    st.session_state.cur.execute('select * from alerts')
    alerts = st.session_state.cur.fetchall()
    df = {'Link':[],'Value':[]}
    for i in alerts:
        if i[0] == username:
            df['Link'].append(i[1])
            df['Value'].append(i[2])
    df = pd.DataFrame(df)
    df.index = range(1,len(list(df['Link']))+1)
    st.markdown('<h2>Alerts</h2>',unsafe_allow_html=True)
    st.dataframe(df,use_container_width=True)

if  page == 'You Ask We Say':
    st.markdown(custom_text_css, unsafe_allow_html=True)
    st.header('Welcome '+ str(username) +'!!!')  # Use username passed as an argument
    st.markdown(custom_text_css, unsafe_allow_html=True)
    prod = st.text_input('Enter the name or type of Product : ')
    cols = st.columns(5)
    review_extracter = Review_Extract()
    sentiment_analysis = Sentiment_Analysis("cardiffnlp/twitter-roberta-base-sentiment")
    fake_review_filter = Fake_Review_Analysis()
    col = st.columns(5)
    with col[4]:
        b = st.button('Start')
    if b and prod != '':
        links1,titls1 = search_and_extract_amazon(prod)
        links2,titls2 = search_and_extract_flipkart(prod)
        st.dataframe(pd.DataFrame({'Titles':titls,'Links':links}),use_container_width=True)
    
  
# with st.spinner('Please wait..'):
#     sleep(3)
# with st.status("Analyzing Products ....",expanded=True):
#     st.write('Gathering Info....')
#     l,t = search_and_extract_amazon(key)
#     try:
#         #Review_Extraction
#         rev = []
#         fairness = []
#         sent_score = []
#         review_extracter.launch()
#         for link,title in zip(l,t):
#             i = l.index(link)+1
#             st.write(f'{i}. Extracting Reviews for {title} .... ')
#             try:
#                 reviews = review_extracter.start(link)
#                 pos = False
#             except Exception as e:
#                 print(e)
#                 reviews = pd.DataFrame([])
#                 pos = True
#             if pos:
#                 st.error(f'Unable to Extract Reviews for {title}')
#             elif reviews.empty:
#                 st.error(f"Product {title} Doesnot have any Reviews")
#             else:
#                 #Price Analysis
#                 st.write(f"Performing Price Analysis for {title}...")
#                 f = review_extracter.price_cal(url=link,bulk=True)
#                 if f == -1:
#                     fairness.append('NetWork Error')
#                 else:
#                     fairness.append(f)
#                 #Fake Review Detection
#                 #st.write("Filtering out Bot Generated Fake Reviews ...")
#                 geniune_reviews = fake_review_filter.filter(reviews)
#                 #st.write("Filtering out Human Generated Fake Reviews ...")
#                 #sleep(5)
#                 #Sentiment Analysis
#                 st.write(f"Analyzing Sentiment for {title}...")
#                 outs = list(sentiment_analysis.start(geniune_reviews))
#                 #st.write(outs[0])
#                 #st.plotly_chart(outs[1],use_container_width=True)
#                 #st.write(outs[2])
#                 #if outs[3] != '':
#                     #st.pyplot(outs[3],use_container_width=True)
#                 positive_weight = 1
#                 neutral_weight = 0.5
#                 negative_weight = -1
#                 positive, negative,neutral = outs[-1]
#                 weighted_sum = (positive * positive_weight) + (neutral * neutral_weight) + (negative * negative_weight)
# 
#                 total_reviews = positive + neutral + negative
#                 try:
#                     score = max((weighted_sum / (total_reviews * (positive_weight + neutral_weight + negative_weight))) * 100,79)
#                 except:
#                     score  = 0
#                 sent_score.append(score)
#                 #st.markdown('<h4>Sentiment Score : </h4>', unsafe_allow_html=True)
#                 #st.write("Price Fairness : "+str(review_extracter.fairness))
#                 grade=0.6*score+0.4*f
#                 if grade<=20:
#                     #st.markdown('<div style="text-align: center;"><span style="font-size: 5em;">D</span></div>',unsafe_allow_html=True)
#                     rev.append("D")
#                 elif grade<=40:
#                     #st.markdown('<div style="text-align: center;"><span style="font-size: 5em;">C</span></div>',unsafe_allow_html=True)
#                     rev.append("C")
#                 elif grade<=60:
#                     #st.markdown('<div style="text-align: center;"><span style="font-size: 5em;">B</span></div>',unsafe_allow_html=True)
#                     rev.append("B")
#                 elif grade<=80:
#                     #st.markdown('<div style="text-align: center;"><span style="font-size: 5em;">A</span></div>',unsafe_allow_html=True)
#                     rev.append("A")
#                 else:
#                     #st.markdown('<div style="text-align: center;"><span style="font-size: 5em;">S</span></div>',unsafe_allow_html=True)
#                     rev.append("S")
#         print(t)
#         print(rev)
#         print(fairness)
#         d = pd.DataFrame({'Title':t, 'Sentiment Score': sent_score,'Price Fairness':fairness, 'Grade':rev})
#         st.dataframe(d,use_container_width=True)
#         review_extracter.finish()
#     except Exception as e:                
#         st.error(e)
