from your_flask_app import db
from your_flask_app.models import Appointment

# Create a new appointment
new_appointment = Appointment(
    student_id=1,  # Replace with actual student ID
    advisor_id=2,  # Replace with actual advisor ID
    datetime='2025-04-02 10:30:00'  # Replace with the correct datetime format
)

# Add to the database session
db.session.add(new_appointment)

# Commit the changes to save the appointment
db.session.commit()

print("Appointment successfully added!")
