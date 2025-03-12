from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from flask_migrate import Migrate

# Initialize db and migrate instances
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)
    
    # Initialize db and migrate with the app
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Import models to register them with the database
        from . import models  # Ensure models are imported so tables are created
        # No need to call db.create_all() here if using migrations

        # Import and register routes
        from .routes import init_routes
        init_routes(app)

    return app

'''db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        from . import models  # Ensure models are imported to create tables
        db.create_all()

        # Import and register routes
        from .routes import init_routes
        init_routes(app)

    return app'''


