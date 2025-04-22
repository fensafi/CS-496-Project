import pandas as pd
import re
from collections import defaultdict

class CourseRecommendationChatbot:
    def __init__(self, courses_file, prerequisites_file, faq_file):
        """Initialize the chatbot with file paths to the CSV data."""
        self.courses_file = courses_file
        self.prerequisites_file = prerequisites_file
        self.faq_file = faq_file
        self.course_data = {}
        self.prerequisite_data = defaultdict(list)
        # New: Track which courses require each course as a prerequisite
        self.required_for = defaultdict(list)
        self.faq_data = {}
        self.load_data()
        
    def load_data(self):
        """Load data from CSV files."""
        try:
            # Load courses data
            courses_df = pd.read_csv(self.courses_file)
            for _, row in courses_df.iterrows():
                self.course_data[row['course_code']] = {
                    "name": row['course_name'],
                    "credits": row['credits'],
                    "description": row['description']
                }
            
            # Load prerequisites data
            prereq_df = pd.read_csv(self.prerequisites_file)
            for _, row in prereq_df.iterrows():
                course = row['course_code']
                prereq = row['prerequisite_code']
                
                # Add to prerequisite mapping
                self.prerequisite_data[course].append(prereq)
                
                # Add to reverse mapping (what this prereq is required for)
                self.required_for[prereq].append(course)
            
            # Load FAQ data
            faq_df = pd.read_csv(self.faq_file)
            for _, row in faq_df.iterrows():
                self.faq_data[row['question'].lower()] = row['answer']
            
            print("Data loaded successfully!")
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def get_course_info(self, course_code):
        """Get information about a specific course."""
        if course_code in self.course_data:
            course = self.course_data[course_code]
            prereqs = self.prerequisite_data.get(course_code, [])
            unlocks = self.required_for.get(course_code, [])
            
            info = f"Course: {course_code} - {course['name']}\n"
            info += f"Credits: {course['credits']}\n"
            info += f"Description: {course['description']}\n"
            
            if prereqs:
                info += "Prerequisites:\n"
                for prereq in prereqs:
                    if prereq in self.course_data:
                        info += f"  - {prereq}: {self.course_data[prereq]['name']}\n"
                    else:
                        info += f"  - {prereq}\n"
            else:
                info += "This course has no prerequisites.\n"
                
            if unlocks:
                info += "This course is a prerequisite for:\n"
                for course in unlocks:
                    if course in self.course_data:
                        info += f"  - {course}: {self.course_data[course]['name']}\n"
                    else:
                        info += f"  - {course}\n"
                
            return info
        else:
            return f"Course {course_code} not found."
    
    def check_prerequisites_met(self, course_code, taken_courses):
        """Check if prerequisites for a course are met."""
        if course_code not in self.prerequisite_data:
            return True, []  # No prerequisites
        
        prereqs = self.prerequisite_data[course_code]
        missing_prereqs = [prereq for prereq in prereqs if prereq not in taken_courses]
        
        return len(missing_prereqs) == 0, missing_prereqs
    
    def get_available_courses(self, taken_courses):
        """Get list of courses available to take based on completed courses."""
        available_courses = []
        
        for course_code in self.course_data:
            if course_code not in taken_courses:
                prereqs_met, missing_prereqs = self.check_prerequisites_met(course_code, taken_courses)
                if prereqs_met:
                    available_courses.append(course_code)
        
        return available_courses
    
    def prioritize_courses(self, available_courses, taken_courses):
        """
        Prioritize courses based on:
        1. Direct next steps (courses that have student's completed courses as direct prerequisites)
        2. CS courses vs non-CS
        3. Course level (lower numbers first)
        """
        # Create category lists
        direct_next_steps = []
        other_cs_courses = []
        other_courses = []
        
        for course in available_courses:
            # Check if this course has any of the taken courses as direct prerequisites
            has_taken_prereq = any(prereq in taken_courses for prereq in self.prerequisite_data.get(course, []))
            
            if has_taken_prereq:
                direct_next_steps.append(course)
            elif course.startswith('CS'):
                other_cs_courses.append(course)
            else:
                other_courses.append(course)
        
        # Sort each category
        direct_next_steps.sort()
        other_cs_courses.sort()
        other_courses.sort()
        
        # Combine in priority order
        prioritized_courses = direct_next_steps + other_cs_courses + other_courses
        return prioritized_courses
    
    def recommend_courses(self, taken_courses):
        """Recommend courses based on completed courses."""
        available_courses = self.get_available_courses(taken_courses)
        
        if not available_courses:
            return "Based on the courses you've taken, I don't have any additional course recommendations."
        
        # Prioritize courses
        prioritized_courses = self.prioritize_courses(available_courses, taken_courses)
        
        recommendation = "Based on the courses you've taken, here are some recommendations:\n\n"
        
        # Find direct next steps from taken courses
        direct_next_steps = []
        for course in taken_courses:
            for next_course in self.required_for.get(course, []):
                if next_course in prioritized_courses:
                    direct_next_steps.append(next_course)
        
        # If we have direct next steps, highlight them
        if direct_next_steps:
            recommendation += "RECOMMENDED NEXT STEPS (courses that build on what you've taken):\n"
            count = 0
            for course in direct_next_steps[:3]:  # Limit to top 3
                recommendation += f"{self.get_course_info(course)}\n"
                count += 1
                
            recommendation += "\nADDITIONAL AVAILABLE COURSES:\n"
            # Get remaining courses for recommendations
            remaining_courses = [c for c in prioritized_courses if c not in direct_next_steps[:3]]
            
            # Add up to 3 more courses to reach a total of 5
            for course in remaining_courses[:5-count]:
                recommendation += f"{self.get_course_info(course)}\n"
        else:
            # Just show top 5 available courses
            for course in prioritized_courses[:5]:
                recommendation += f"{self.get_course_info(course)}\n"
        
        return recommendation
    
    def answer_faq(self, question):
        """Answer frequently asked questions."""
        # Simple keyword matching
        question_lower = question.lower()
        
        for faq_question, answer in self.faq_data.items():
            if any(keyword in question_lower for keyword in faq_question.lower().split()):
                return f"Q: {faq_question}\nA: {answer}"
        
        return "I'm sorry, I don't have an answer to that question. Please try asking about course recommendations or check our FAQ page."
    
    def parse_courses_input(self, input_text):
        """Parse the input text to extract course codes."""
        # Extract course codes using regex
        pattern = r'\b[A-Z]{2,4}\d{3}\b'
        courses = re.findall(pattern, input_text.upper())
        
        # Remove duplicates while preserving order
        unique_courses = []
        for course in courses:
            if course not in unique_courses and course in self.course_data:
                unique_courses.append(course)
        
        return unique_courses
    
    def process_input(self, user_input):
        """Process user input and generate appropriate response."""
        # Check if the input is asking for course recommendations
        if re.search(r'\b(recommend|suggest|what|which|courses|class|classes)\b', user_input.lower()) and re.search(r'\b(take|taken|completed|finished|done)\b', user_input.lower()):
            taken_courses = self.parse_courses_input(user_input)
            
            if taken_courses:
                return self.recommend_courses(taken_courses)
            else:
                return "Please specify which courses you have taken. For example: 'I have taken CS180 and MATH136, what courses should I take next?'"
        
        # Check if input is asking for specific course information
        course_match = re.search(r'\b([A-Z]{2,4}\d{3})\b', user_input.upper())
        if course_match and re.search(r'\b(what is|tell me about|info|information|details)\b', user_input.lower()):
            course_code = course_match.group(1)
            return self.get_course_info(course_code)
        
        # Check for FAQ questions
        for word in ['how', 'what', 'when', 'where', 'why', 'can', 'do', 'does', 'prerequisite', 'drop']:
            if word in user_input.lower():
                faq_response = self.answer_faq(user_input)
                if "I'm sorry" not in faq_response:
                    return faq_response
        
        # Default response for unrecognized input
        return "I can help you with course recommendations and FAQs. Try asking:\n1. 'What courses should I take after completing CS180 and MATH136?'\n2. 'Tell me about CS290'\n3. 'How do I drop a class?'"


def main():
    # File paths
    courses_file = 'courses.csv'
    prerequisites_file = 'prerequisites.csv'
    faq_file = 'faq.csv'
    
    # Initialize the chatbot
    chatbot = CourseRecommendationChatbot(courses_file, prerequisites_file, faq_file)
    
    print("Welcome to the Course Recommendation Chatbot!")
    print("Type 'exit' or 'quit' to end the conversation.")
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Chatbot: Goodbye! Have a great day.")
            break
        
        response = chatbot.process_input(user_input)
        print(f"\nChatbot: {response}")


if __name__ == "__main__":
    main()