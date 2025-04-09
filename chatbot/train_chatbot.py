import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
from utils import fetch_faq

nltk.download('punkt')
nltk.download('stopwords')

def clean(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    return [word for word in tokens if word not in stop_words and word not in string.punctuation]

def train_faq_data():
    faq_data = fetch_faq()
    training_data = []

    for question, answer in faq_data:
        tokens = clean(question)
        training_data.append((tokens, answer))

    return training_data
