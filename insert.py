from app import create_app, db
from app.models import Student
from werkzeug.security import generate_password_hash

# Create Flask app instance
app = create_app()

# Use the application context
with app.app_context():
    student = Student(name="Test Student", email="test@example.com")
    student.password = generate_password_hash("password123")

    # Add user to database
    db.session.add(student)
    db.session.commit()

    print("Student inserted successfully!")
