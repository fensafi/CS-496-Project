from app import create_app, db
from app.models import Administration  # Assuming the Administration model exists
from werkzeug.security import generate_password_hash

# Create Flask app instance
app = create_app()

# Use the application context
with app.app_context():
    # Create new admin
    admin = Administration(
        name="Test Admin",
        email="ad@example.com",
        password=generate_password_hash("pass")  # Hash the password
    )

    # Add admin to database
    db.session.add(admin)
    db.session.commit()

    print("Admin inserted successfully! Email: admin@example.com")
