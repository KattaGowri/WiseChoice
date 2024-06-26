from joblib import load
import pandas as pd
import string,nltk

class Fake_Review_Analysis:
    
    def __init__(self):
        self.model = load(open(r"fake_review.joblib", 'rb'))

    def filter(self,df):
        l=[]

        for index, row in df.iterrows():
            row_series = pd.Series(row)
            prediction = self.model.predict(row_series.values.reshape(1, -1))[0]
            if prediction == "OR":
                l.append(row)
        return pd.DataFrame(l,columns=['Review'])
        

