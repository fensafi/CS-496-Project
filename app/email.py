from flask_mail import Message
from app import mail
from threading import Thread
from flask import current_app

def send_async_email(msg):
    # Use current_app.app_context() to properly push the app context
    with current_app.app_context():  
        mail.send(msg)

def send_appointment_confirmation(student_email, appointment_data):
    msg = Message(
        "Your Appointment Confirmation",
        recipients=[student_email]
    )

    msg.body = f"""
    Dear Student,

    Your appointment with {appointment_data['advisor_name']}
    has been scheduled for {appointment_data['appointment_time']}.
    """
    
    # Start a new thread to send the email asynchronously
    thread = Thread(target=send_async_email, args=(msg,))
    thread.start()
