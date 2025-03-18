from app import create_app, db
from app.models import Advisor  # Import Advisor model
from werkzeug.security import generate_password_hash

# Create Flask app instance
app = create_app()

# Use the application context
with app.app_context():
    # Create a new Advisor instance
    advisor = Advisor(
        name="Test Advisor",
        email="test2@example.com",
        office="Room 101"  # Make sure to provide a value for the office field
    )
    
    # Hash the password and assign it to the advisor
    advisor.password = generate_password_hash("password1234")

    # Add advisor to the database
    db.session.add(advisor)
    db.session.commit()

    print("Advisor inserted successfully!")
