from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        from . import models  # Ensure models are imported to create tables
        db.create_all()

        # Import and register routes
        from .routes import init_routes
        init_routes(app)

    return app

'''from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from .config import Config  # Correct import path

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Use the Config class directly
    db.init_app(app)

    with app.app_context():
        from . import models  # Ensure models are imported to create tables
        db.create_all()

        # Define routes here
        @app.route('/')
        def home():
            return render_template('index.html')

    return app'''

