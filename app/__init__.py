from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import Config
from flask import Flask
from flask_mail import Mail, Message


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config.from_object(Config)

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = app.config['MAIL_USERNAME']
    app.config['MAIL_PASSWORD'] = app.config['MAIL_PASSWORD']
    app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']


    db.init_app(app)  # Initialize the db with the app
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    with app.app_context():
        from . import models  # Import models inside app context to avoid circular import
        from .routes import init_routes
        init_routes(app)
        
        # Clean up expired availabilities after the app is fully initialized
        clean_up_availabilities()

    return app

def clean_up_availabilities():
    """Deletes expired availabilities."""
    from .models import Availability, Appointment  # Import Availability here to avoid circular import
    from datetime import datetime

    now = datetime.now()
    expired_availabilities = Availability.query.filter(Availability.date < now).all()
    expired_appointments = Appointment.query.filter(Appointment.date < now).all()
    
    for avail in expired_availabilities:
        db.session.delete(avail)
    db.session.commit()

    for app in expired_appointments:
        db.session.delete(app)
    db.session.commit()
    print(f"Cleaned up {len(expired_availabilities)} expired availabilities and {len(expired_appointments)}.")
