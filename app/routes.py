from flask import render_template

def init_routes(app):
    @app.route('/')
    def home():
        return render_template('index.html')

'''from flask import render_template
from . import create_app

app = create_app()

@app.route('/')
def home():
    return render_template('index.html')'''

'''from flask import render_template
from . import app  # Use the app instance from __init__.py

@app.route('/')
def home():
    return render_template('index.html')'''