from joblib import load
import pandas as pd
import csv
import string,nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
nltk.download('stopwords')

def text_process(review):
    nopunc = [char for char in review if char not in string.punctuation]
    nopunc = ''.join(nopunc)
    return [word for word in nopunc.split() if word.lower() not in stopwords.words('english')]

class Fake_Review_Analysis:


    def predict_and_filter(self,original_dataframe, model):
        # Create an empty DataFrame for storing rows with "OG" prediction
        l=[]

        # Iterate through each row of the original DataFrame
        for index, row in original_dataframe.iterrows():
            # Convert the row to a Pandas Series object
            row_series = pd.Series(row)

            # Use the model to make a prediction
            prediction = model.predict(row_series.values.reshape(1, -1))[0]

            # Check if the prediction is "OG"
            if prediction == "OR":
                l.append(row)
        return pd.DataFrame(l)
        
    def extract(self,reviews):
        model = load(open(r"fake_review.joblib", 'rb'))
        df = reviews
        return self.predict_and_filter(df,model)
