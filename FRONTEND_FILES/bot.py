from dotenv import load_dotenv
import re
load_dotenv()

import google.generativeai as genai

class GeminiTerminalApp:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-pro")
        self.chat = self.model.start_chat(history=[])
        genai.configure(api_key="AIzaSyCYDGQXaq8b69eR4LJtj0Es7jJAqFGf0GI")
    def remove_emoji(self,text):
  # Define the emoji pattern with raw strings for proper unicode support
      emoji_pattern = re.compile(r"""
        \U0001F600-\U0001F64F  # emoticons
        |\U0001F300-\U0001F5FF  # symbols & pictographs
        |\U0001F680-\U0001F6FF  # emoticons (supplemental)
        |\U0001F1E0-\U0001F1FF  # flags (supplemental)
        |\U00002702-\U000027B0  # dingbats
        |\U000024C2-\U00001F251  # additional emoticons
        """, flags=re.UNICODE)
      return emoji_pattern.sub('', text)
    
    def get_gemini_response(self, question):
        response = self.chat.send_message(question, stream=True)
        return response

    def run(self,user_input):
        response = self.get_gemini_response(user_input)
        res = ''
        for chunk in response:
            res += (chunk.text)
        return res

def process(data):
    app = GeminiTerminalApp()
    data=app.remove_emoji(data)
    data = app.run("Summarize this into 5 pros and 5 cons"+data)
    return data
