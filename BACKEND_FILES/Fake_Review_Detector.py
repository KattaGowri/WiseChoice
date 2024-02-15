from joblib import load
import pandas as pd
import string,nltk

class Fake_Review_Analysis:
    
    def __init__(self):
        self.model = load(open(r"fake_review.joblib", 'rb'))

    def filter(self,df):
        # Create an empty DataFrame for storing rows with "OG" prediction
        l=[]

        # Iterate through each row of the original DataFrame
        for index, row in df.iterrows():
            # Convert the row to a Pandas Series object
            row_series = pd.Series(row)

            # Use the model to make a prediction
            prediction = self.model.predict(row_series.values.reshape(1, -1))[0]

            # Check if the prediction is "OG"
            if prediction == "OR":
                l.append(row)
        return pd.DataFrame(l,columns=['Review'])
        

