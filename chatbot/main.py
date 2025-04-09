print("main is running")
from chatbot import find_best_faq_response, recommend_courses

def run_chatbot():
    print("Welcome to the Advising Assistant! Type 'quit' to exit.")
    
    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "quit":
            print("Goodbye!")
            break

        response = find_best_faq_response(user_input)
        if response:
            print(f"Advisor Bot: {response}")
        else:
            print("Advisor Bot: What courses have you taken? (comma-separated)")
            taken = input("You: ").strip().split(",")
            taken = [c.strip().upper() for c in taken]
            recs = recommend_courses(taken)
            
            if recs:
                print("Advisor Bot: Based on your courses, consider these:")
                for code, name, desc in recs:
                    print(f"- {code}: {name} – {desc}")
            else:
                print("Advisor Bot: I couldn’t find any course recommendations with those prerequisites.")

if __name__ == "__main__":
    run_chatbot()
