from flask_mail import Message
from app import mail
from threading import Thread
from flask import current_app

def send_async_email(app, msg):
    with app.app_contact():
        mail.send(msg)

def send_appointment_confirmation(student_email, appointment_data):

    msg = Message(
        "Your Appointment Confirmation",
        recipients=[student_email]
    )

    msg.body = f"""
    Dear Studnet,

    Your appointment with {appointment_data['advisor_name']}
    has been scheduled for {appointment_data['appointment_time']}. 
    """
    
    Thread(
        target=send_async_email,
        args=(current_app.get_current_object(), msg)
    ).start()