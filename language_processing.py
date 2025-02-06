from textblob import TextBlob
from dataclasses import dataclass

    
def get_mood(input_text:str):
    sentiment:float = TextBlob(input_text).sentiment.polarity

    return sentiment
    