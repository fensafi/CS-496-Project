from flask import render_template, request, redirect, url_for, flash, session
from .models import Student, Advisor, Administration
from . import db
from flask_login import login_required, login_user, logout_user, LoginManager

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

            # Check Students table
            user = Student.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user)
                session['user_type'] = 'student'
                session['user_id'] = user.student_id  # Store student ID in session
                return redirect(url_for('student_dashboard'))

            # Check Advisors table
            user = Advisor.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user)
                session['user_type'] = 'advisor'
                session['user_id'] = user.advisor_id  # Store advisor ID in session
                return redirect(url_for('advisor_dashboard'))

            # Check Administration table (No changes)
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
            student = Student.query.filter_by(student_id=session.get('user_id')).first()
            return render_template('student_dashboard.html', student=student)
        return redirect(url_for('login'))


    @app.route('/advisor_dashboard')
    def advisor_dashboard():
        if session.get('user_type') == 'advisor':
            advisor = Advisor.query.filter_by(advisor_id=session.get('user_id')).first()
            return render_template('advisor_dashboard.html')
        return redirect(url_for('login'))

    @app.route('/admin_dashboard', methods=['GET', 'POST'])
    @login_required
    def admin_dashboard():
        if session.get('user_type') != 'admin':
            return redirect(url_for('login'))

        # Fetch all users
        students = Student.query.all()
        advisors = Advisor.query.all()
        admins = Administration.query.all()

        return render_template('admin_dashboard.html', students=students, advisors=advisors, admins=admins)

    @app.route('/admin/create_user', methods=['POST'])
    @login_required
    def create_user():
        if session.get('user_type') != 'admin':
            return redirect(url_for('login'))

        user_type = request.form.get('user_type')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')

        if user_type == "student":
            new_user = Student(student_id=int(request.form.get('student_id')), first_name=first_name, last_name=last_name, email=email)
        elif user_type == "advisor":
            new_user = Advisor(advisor_id=int(request.form.get('advisor_id')), first_name=first_name, last_name=last_name, email=email, office=request.form.get('office'))
        elif user_type == "admin":
            new_user = Administration(name=f"{first_name} {last_name}", email=email)

        new_user.set_password(password)  # Hash the password
        db.session.add(new_user)
        db.session.commit()

        flash(f'{user_type.capitalize()} {first_name} {last_name} created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/delete_user/<user_type>/<int:user_id>', methods=['POST'])
    @login_required
    def delete_user(user_type, user_id):
        if session.get('user_type') != 'admin':
            return redirect(url_for('login'))

        if user_type == "student":
            user = Student.query.get(user_id)
        elif user_type == "advisor":
            user = Advisor.query.get(user_id)
        elif user_type == "admin":
            user = Administration.query.get(user_id)

        if user:
            db.session.delete(user)
            db.session.commit()
            flash(f'{user_type.capitalize()} deleted successfully!', 'success')
        else:
            flash(f'User not found!', 'danger')

        return redirect(url_for('admin_dashboard'))
