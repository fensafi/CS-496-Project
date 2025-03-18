from flask import render_template, request, redirect, url_for, flash, session
from .models import Student, Advisor, Administration
from . import db
from flask_login import login_user, logout_user, LoginManager

login_manager = LoginManager()

def init_routes(app):
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        # Try loading user from each table
        user = Student.query.get(user_id) or Advisor.query.get(user_id) or Administration.query.get(user_id)
        return user

    @app.route('/')
    @app.route('/home')
    def home():
        return render_template('home.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            # Check in Students table
            user = Student.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user)
                session['user_type'] = 'student'
                return redirect(url_for('student_dashboard'))

            # Check in Advisors table
            user = Advisor.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user)
                session['user_type'] = 'advisor'
                return redirect(url_for('advisor_dashboard'))

            # Check in Administration table
            user = Administration.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user)
                session['user_type'] = 'admin'
                return redirect(url_for('admin_dashboard'))

            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        logout_user()
        session.pop('user_type', None)
        return redirect(url_for('home'))

    @app.route('/student_dashboard')
    def student_dashboard():
        if session.get('user_type') == 'student':
            return render_template('student_dashboard.html')
        return redirect(url_for('login'))

    @app.route('/advisor_dashboard')
    def advisor_dashboard():
        if session.get('user_type') == 'advisor':
            return render_template('advisor_dashboard.html')
        return redirect(url_for('login'))

    @app.route('/admin_dashboard')
    def admin_dashboard():
        if session.get('user_type') == 'admin':
            return render_template('admin_dashboard.html')
        return redirect(url_for('login'))
