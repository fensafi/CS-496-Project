from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import Config
from flask_mail import Mail
from flask_babel import Babel, _
import os
from sqlalchemy import inspect






db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
babel = Babel()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config.from_object(Config)

    # Email configs
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = app.config['MAIL_USERNAME']
    app.config['MAIL_PASSWORD'] = app.config['MAIL_PASSWORD']
    app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']


    # Babel configs
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(basedir, 'translations')
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'es']


    # Initializations
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    # Clean up availabilities
    with app.app_context():
        from . import models
        from .routes import init_routes
        init_routes(app)
        
        try:
            clean_up_availabilities()
        except Exception as e:
            print(f"Warning: Failed to clean up availabilities: {e}")

    # Bable initilization
    babel.init_app(app, locale_selector=get_locale)

    @app.context_processor
    def inject_translations():
        return dict(_=_)


    # Blueprint routes
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

def clean_up_availabilities():
    # Imports here to avoid circular import
    from .models import Availability, Appointment
    from datetime import datetime

    inspector = inspect(db.engine)
    if 'availabilities' in inspector.get_table_names() and 'appointments' in inspector.get_table_names():
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
    else:
        print("Tables not yet created; skipping cleanup.")

# Babel thing
def get_locale():
    return session.get('lang', 'en')


