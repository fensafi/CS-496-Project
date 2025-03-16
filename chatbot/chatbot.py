import psycopg2
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import string

#download nltk resources 
nltk.download('punkt')
nltk.download('stopwords')

#Postgres connection
DB_NAME = "wku_cs_advising"
DB_USER ="postgres"
DB_PASS = "root"
DB_HOST = "localhost"
DB_PORT = "5432"

# initialize NLP tools
stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

def connect_db():
    """Establishes a connection the the PostgreSQL database"""
    return psycopg2.connect(
        dbname=DB_NAME, 
        user=DB_USER, 
        password=DB_PASS, 
        host=DB_HOST, 
        port=DB_PORT
    )

def preprocess_text(text):
    """tokenizes, removes stopwords, and stems input text for better matching"""
    text = text.lower()
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_Words and word not in string.punctuation]
    tokens = [stemmer.stem(word) for word in tokens]
    return " ".join(tokens)

def get_response(text):
    '''fetches chatbot response from the database'''
    processed_input = preprocess_text(user_input)
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT response FROM faq WHERE question ILIKE %s", ('%' + processed_input + '%',))
    result = cur.fetchone()

    conn.close()

    return result[0] if result else "I'm not sure. Please check with your advisor by scheduling an appointment."

def add_response(question, answer):
    '''adds a new question-answer pair to the db'''
    conn = connect_db()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO faq (question, answer) VALUES (%s, %s) ON CONFLICT (question) DO UPDATE SET answer = EXCLUDE.answer", (question, answer))
        conn.commit()

        return "New response added successfully!"
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()

if __name__ == "__main__":
    print("Student Advisor Bot: Hello! How can I help you today?")
    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Student Advisor Bot: Goodbye!")
            break

        elif user_input.lower().startswith("add question:"):
            parts = user_input.split("||")
            if len(parts) == 3:
                question = parts[1].strip()
                answer = parts[2].strip()
                response = add_response(question, answer)
            else:
                reponse = "To add a question, use the format 'add question: || <question> || <answer>'"
        else:
            response = get_response(user_input)

        print(f"Student Advisor Bot: {response}")