import pytest
from chatbot import CourseRecommendationChatbot

@pytest.fixture
def chatbot():
    # creates a chatbot instance with test data
    return CourseRecommendationChatbot(
        courses_file='chatbot/tests/test_courses.csv',
        prerequisites_file='chatbot/tests/prerequisites.csv',
        faq_file='chatbot/tests/test_faq.csv'
    )

def test_course_info(chatbot):
    # tests getting course info
    response = chatbot.get_course_info("CS290")
    assert "CS290" in response
    assert "Computer Science II" in response

def test_prerequisites(chatbot):
    # tests prerequisites
    met, missing = chatbot.check_prerequisites_met("CS270", ["CS180"])
    assert met is True
    met, missing = chatbot.check_prerequisites_met("CS270", [""])
    assert met is False
    assert "CS180" in missing

def test_recommendations(chatbot):
    # tests course recommendations
    response = chatbot.recommend_courses(["CS180"])
    assert "CS270" in response

def test_faq(chatbot):
    # test FAQ
    response = chatbot.answer_faq("How do I schedule an appointment?")
    assert "schedule" in response.lower()

def test_input_parsing(chatbot):
    # test input parsing
    courses = chatbot.parse_courses_input("I've taken CS290 and CS180")
    assert "CS290" in courses
    assert "CS180" in courses

def test_unknown_input(chatbot):
    # testing for random input that will redirect the user to stay in topic
    response = chatbot.answer_faq("So today i walked a mile")
    assert "so" in response
