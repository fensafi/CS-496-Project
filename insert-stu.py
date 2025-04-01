from app import create_app, db
from app.models import Student
from werkzeug.security import generate_password_hash
import random

# Create Flask app instance
app = create_app()

# Use the application context
with app.app_context():
    # Generate a random 9-digit student ID starting with 801
    student_id = "801" + str(random.randint(100000, 999999))

    # Create new student
    student = Student(
        first_name="Test",
        last_name="Student",
        student_id=student_id,  # Assuming student_id is stored as a string
        email="test@example.com",
        password=generate_password_hash("password123")
    )

    # Add student to database
    db.session.add(student)
    db.session.commit()

    print(f"Student inserted successfully! Student ID: {student_id}")
