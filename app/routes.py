from flask import render_template


def init_routes(app):
    @app.route('/')
    
    @app.route('/home')
    def home():
        return render_template('home.html')

    @app.route('/login')
    def login():
        return render_template('login.html')

    



