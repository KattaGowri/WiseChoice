import pandas as pd
import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
import plotly.graph_objs as go
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from scipy.special import softmax


class Sentiment_Analysis:
    def __init__(self,model):
        self.token = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForSequenceClassification.from_pretrained(model)
        self.sentiments = ['Negative','Neutral','Positive']
        
    def preprocess_text(self,text):
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


    def sentiment_analyse(self,text):
        out = self.token(text,return_tensors='pt')
        out = self.model(**out)
        score = out[0][0].detach().numpy()
        score = list(softmax(score))
        return score.index(max(score))
    
    def start(self,df):
        df = df.dropna()
        yield (f"There are a total of {df.shape[0]} reviews given")
        df.columns = ["Review"]
        data = df.copy()
        data["Review"].apply(self.preprocess_text)
        count_positive = 0
        count_negative = 0
        count_neutral = 0
        sentiments = []
        for i in df.iterrows():
            rev = list(i[1])[0]
            if rev == '':
                continue
            try:
                rev = rev[:1500]
            except:
                pass
            res = self.sentiment_analyse(rev)
            sentiments.append(self.sentiments[res])
            if res==0:
                count_negative+=1
            elif res==1:
                count_neutral+=1
            else:
                count_positive+=1
            

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
        yield fig
        yield f"Positive: {count_positive}, Negative: {count_negative}, Neutral: {count_neutral}"
        
        # Word Cloud
        wordcloud_data = " ".join(df["Review"].astype(str))
        wordcloud = WordCloud(width=800, height=400, max_words=100, background_color="#f6f5f6", colormap='viridis').generate(wordcloud_data)

        # Set the color scheme of the Word Cloud
        wordcloud.recolor(color_func=lambda *args, **kwargs: "#8d7995")

        fig_wordcloud = plt.figure(figsize=(8, 4), facecolor="#f6f5f6")
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title('Word Cloud - Most Frequent Words', color='#0e0d0e')  # Set text color
        plt.gca().set_facecolor("#f6f5f6")  # Set background color for the entire plot
        yield fig_wordcloud


        df["Sentiment"] = sentiments
        yield df
        
        
# if st.button('click'):
#     
#     obj = Sentiment_Analysis()
#     obj.start(pd.read_csv('scrapedReviews.csv'))

