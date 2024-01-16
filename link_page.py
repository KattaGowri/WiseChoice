import streamlit as st
from time import sleep
import Review_Extraction,pickle,csv,string,re,nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
import plotly.graph_objs as go
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from joblib import load
# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')

custom_text_css = """
    <style>
        .custom-text {
            color: #ffffff;
        }
    </style>
"""

#Fake Review Detection
def text_process(review):
    nopunc = [char for char in review if char not in string.punctuation]
    nopunc = ''.join(nopunc)
    return [word for word in nopunc.split() if word.lower() not in stopwords.words('english')]






def predict_and_filter(original_dataframe, model):
    # Create an empty DataFrame for storing rows with "OG" prediction
    
    l=[]

    # Iterate through each row of the original DataFrame
    for index, row in original_dataframe.iterrows():
        # Convert the row to a Pandas Series object
        row_series = pd.Series(row)

        # Use the model to make a prediction
        prediction = model.predict(row_series.values.reshape(1, -1))[0]

        # Check if the prediction is "OR"
        if prediction == "OR":
            l.append(row)
    return pd.DataFrame(l)
    
def extract(reviews):
    model = load(open(r"fake_review.joblib", 'rb'))
    df = reviews
    return predict_and_filter(df,model)

#Sentiment Analysis
def preprocess_text(text):
    # Make text lowercase and remove links, text in square brackets, punctuation, and words containing numbers
    text = str(text)
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+|\[.*?\]|[^a-zA-Z\s]+|\w*\d\w*', ' ', text)
    text = re.sub(r'\n', ' ', text)

    # Remove stop words
    stop_words = set(stopwords.words("english"))
    words = text.split()
    filtered_words = [word for word in words if word not in stop_words]
    text = ' '.join(filtered_words).strip()

    # Tokenize
    tokens = nltk.word_tokenize(text)

    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    lem_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    return ' '.join(lem_tokens)

def classify_multiple(dataframe):
    st.write(f"There are a total of {dataframe.shape[0]} reviews given")

    dataframe.columns = ["Review"]
    data = dataframe.copy()
    data["Review"].apply(preprocess_text)
    count_positive = 0
    count_negative = 0
    count_neutral = 0
    sentiments = []
    for i in range(dataframe.shape[0]):
        rev = data.iloc[i]
        rev = vect.transform(rev)
        res = model.predict(rev)
        sentiments.append(res)
        if res[0]=='Positive':
            count_positive+=1
        elif res[0]=='Negative':
            count_negative+=1
        else:
            count_neutral+=1 

    x = ["Positive", "Negative", "Neutral"]
    y = [count_positive, count_negative, count_neutral]

    fig = go.Figure()
    layout = go.Layout(
        title='Product Reviews Analysis',
        xaxis=dict(title='Category'),
        yaxis=dict(title='Number of reviews'),
        paper_bgcolor='#f6f5f6',  # Background color
        font=dict(color='#0e0d0e')  # Text color
    )

    fig.update_layout(layout)
    fig.add_trace(go.Bar(name='Multi Reviews', x=x, y=y, marker_color='#8d7995'))  # Bar color
    st.plotly_chart(fig, use_container_width=True)
    st.write(f"Positive: {count_positive}, Negative: {count_negative}, Neutral: {count_neutral}")
    
    # Word Cloud
    wordcloud_data = " ".join(dataframe["Review"].astype(str))
    wordcloud = WordCloud(width=800, height=400, max_words=100, background_color="#f6f5f6", colormap='viridis').generate(wordcloud_data)

    # Set the color scheme of the Word Cloud
    wordcloud.recolor(color_func=lambda *args, **kwargs: "#8d7995")

    fig_wordcloud = plt.figure(figsize=(8, 4), facecolor="#f6f5f6")
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title('Word Cloud - Most Frequent Words', color='#0e0d0e')  # Set text color
    plt.gca().set_facecolor("#f6f5f6")  # Set background color for the entire plot
    st.pyplot(fig_wordcloud, use_container_width=True)


    dataframe["Sentiment"] = sentiments
    st.dataframe(dataframe, use_container_width=True)


with open('user.txt') as f:
    st.markdown(custom_text_css, unsafe_allow_html=True)
    st.header('Welcome '+f.read()+'!!!')
st.markdown(custom_text_css, unsafe_allow_html=True)   
link = st.text_input("Amazon Product Link",placeholder='Enter Product Link here')
col = st.columns(5)
with col[4]:
    b = st.button('Analyze')
if b:
    with st.spinner('Please wait..'):
        sleep(3)
    with st.status("Analyzing Product ....",expanded=True):
        #Review_Extraction
        obj = Review_Extraction.Review_Extract()
        st.write("Extracting Reviews....")
        reviews = obj.start(link)
        if reviews.empty:
            st.error("Product Doesnot have any Reviews")
        else:
            #Price Analysis
            st.write("Performing Price Analysis ...")
            status = obj.price_cal(link)
            obj.finish()
            #Fake Review Detection
            st.write("Filtering out Fake Reviews ...")
            geniune_reviews = extract(reviews)
            #Sentiment Analysis
            st.write("Analyzing Sentiment ...")
            with open("models.p", 'rb') as mod:
                data = pickle.load(mod)
            vect = data['vectorizer']
            model = data["logreg"]
            dataframe = geniune_reviews
            if dataframe.shape[1]!=1:
                st.write("Wrong CSV format!")
            else:
                classify_multiple(dataframe)
            if status:
                st.write("Lowest Price   : "+str(obj.prices['Lowest']))
                st.write("Highest Price  : "+str(obj.prices['Highest']))
                st.write("Average Price  : "+str(obj.prices['Average']))
                st.write("Price Fairness : "+str(obj.fairness))
            else:
                st.write("Price Analysis Not Possible or Failed")
        
        
        
