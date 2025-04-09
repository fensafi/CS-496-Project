from train_chatbot import clean, train_faq_data
from utils import fetch_courses, fetch_prerequisites

faq_data = train_faq_data()

def find_best_faq_response(user_input):
    user_tokens = set(clean(user_input))
    best_match = None
    highest_overlap = 0

    for question_tokens, answer in faq_data:
        overlap = len(user_tokens.intersection(question_tokens))
        if overlap > highest_overlap:
            highest_overlap = overlap
            best_match = answer

    return best_match if highest_overlap > 0 else None

def recommend_courses(taken_courses):
    all_courses = fetch_courses()
    prereqs = fetch_prerequisites()

    taken_set = set(taken_courses)
    recommendations = []

    for code, name, desc in all_courses:
        if code in taken_set:
            continue

        # Get prereqs for this course
        course_prereqs = [pre for course, pre in prereqs if course == code]

        # Recommend if all prereqs are met
        if all(pre in taken_set for pre in course_prereqs):
            recommendations.append((code, name, desc))

    return recommendations
