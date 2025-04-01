from app import create_app, db
from app.models import Advisor  # Assuming the Advisor model exists
from werkzeug.security import generate_password_hash
import random

# Create Flask app instance
app = create_app()

# Use the application context
with app.app_context():
    # Generate a random 9-digit advisor ID starting with 801
    advisor_id = "801" + str(random.randint(100000, 999999))

    # Create new advisor
    advisor = Advisor(
        first_name="Test",
        last_name="Advisor",
        advisor_id=advisor_id,  # Assuming advisor_id is stored as a string
        email="advisor@example.com",
        password=generate_password_hash("password123"),
        office="Office 123"  
    )

    # Add advisor to database
    db.session.add(advisor)
    db.session.commit()

    print(f"Advisor inserted successfully! Advisor ID: {advisor_id}")
