from flask import render_template, request, redirect, url_for, flash, session
from .models import Student, Advisor, Administration
from . import db
from .models import Availability
from flask_login import login_required, login_user, logout_user, LoginManager
from flask import Flask, request, jsonify  # Ensure jsonify is imported
import re
from datetime import datetime
from flask import session

login_manager = LoginManager()

def init_routes(app):
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        # Try loading user from each table
        user = Student.query.get(user_id) or Advisor.query.get(user_id) or Administration.query.get(user_id)
        return user


    ''' Home & Login'''
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


    ''' Student Dashboard'''
    @app.route('/student_dashboard')
    def student_dashboard():
        if session.get('user_type') == 'student':
            student = Student.query.filter_by(student_id=session.get('user_id')).first()
            return render_template('student_dashboard.html', student=student)
        return redirect(url_for('login'))
    
    @app.route('/schedule-appointments')
    def schedule_appointments():
        if session.get('user_type') == 'student':
            student = Student.query.filter_by(student_id=session.get('user_id')).first()
            return render_template('schedule-appointments.html', student=student)
        return redirect(url_for('login'))

    @app.route('/advisors_availability')
    def advisors_availability():
        if session.get('user_type') == 'advisor':
            advsior = Advisor.query.filter_by(advisor_id=session.get('user_id')).first()
            return render_template('advisors_availability.html')
        return redirect(url_for('login'))
    

    ''' Advisor Dashboard'''
    @app.route('/advisor_dashboard')
    def advisor_dashboard():
        if session.get('user_type') == 'advisor':
            advisor = Advisor.query.filter_by(advisor_id=session.get('user_id')).first()
            return render_template('advisor_dashboard.html')
        return redirect(url_for('login'))

    @app.route("/add_availability", methods=["POST"])
    def add_availability():
        try:
            data = request.get_json()
            print("Received data:", data)  # Debugging output

            selected_date = data.get("date")
            selected_time = data.get("time")
            advisor_email = data.get("email")  # Get the email from the session

            # Debugging prints
            print(f"Extracted values - Date: {selected_date}, Time: {selected_time}, Advisor Email: {advisor_email}")

            # Ensure required fields are present
            if not selected_date:
                print("Error: Missing selected_date")
                return jsonify({"message": "Missing date"}), 400
            if not selected_time:
                print("Error: Missing selected_time")
                return jsonify({"message": "Missing time"}), 400
            if not advisor_email:
                print("Error: Missing advisor_email")
                return jsonify({"message": "Missing advisor email"}), 400

            # Validate and format datetime
            try:
                selected_datetime = datetime.strptime(f"{selected_date} {selected_time}", "%Y-%m-%d %I:%M %p")
            except ValueError as e:
                print(f"Datetime Parsing Error: {str(e)}")
                return jsonify({"message": f"Invalid datetime format: {str(e)}"}), 400

            # Create availability record (only storing email and datetime)
            availability = Availability(
                advisor_email=advisor_email,
                datetime=selected_datetime  # ✅ Use datetime instead of separate date/time fields
            )

            # Save to database
            db.session.add(availability)
            db.session.commit()

            print(f"Saved availability: {selected_datetime}")  # Debugging output

            return jsonify({"message": "Availability added successfully!"}), 200

        except Exception as e:
            db.session.rollback()  # Rollback transaction on error
            print(f"Error: {str(e)}")
            return jsonify({"message": "Error while adding availability."}), 500


    ''' Admin Dashboard'''
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
    
    # Create User 
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
    
    # Delete User
    @app.route('/admin/delete_user/<user_type>/<int:user_id>', methods=['POST'])
    @login_required
    def delete_user(user_type, user_id):
        print(f"DEBUG: Entering delete_user route with user_type: {user_type}, user_id: {user_id}")

        # Check if the current user is an admin
        if session.get('user_type') != 'admin':
            print("DEBUG: User is not an admin, redirecting to login.")
            return redirect(url_for('login'))

        # Dynamically select the appropriate table and column based on user_type
        if user_type == "student":
            print("DEBUG: Attempting to delete a student.")
            user = Student.query.filter_by(student_id=user_id).first()
        elif user_type == "advisor":
            print("DEBUG: Attempting to delete an advisor.")
            user = Advisor.query.filter_by(advisor_id=user_id).first()
        elif user_type == "admin":
            print("DEBUG: Attempting to delete an admin.")
            user = Administration.query.filter_by(id=user_id).first()
        else:
            print(f"DEBUG: Invalid user_type received: {user_type}")
            flash('Invalid user type!', 'danger')
            return redirect(url_for('admin_dashboard'))

        # Check if the user was found
        if user:
            print(f"DEBUG: User found: {user}")
            try:
                db.session.delete(user)
                db.session.commit()
                print(f"DEBUG: {user_type.capitalize()} with ID {user_id} deleted successfully.")
                flash(f'{user_type.capitalize()} deleted successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                print(f"DEBUG: Error while deleting user: {e}")
                flash(f'Error deleting {user_type}: {str(e)}', 'danger')
        else:
            print(f"DEBUG: No {user_type} found with ID {user_id}.")
            flash(f'{user_type.capitalize()} not found!', 'danger')

        return redirect(url_for('admin_dashboard'))

    # Search User
    @app.route('/admin/search_users', methods=['GET'])
    @login_required
    def search_users():
        if session.get('user_type') != 'admin':
            return redirect(url_for('login'))

        query = request.args.get('query', '').strip()

        if not query:
            flash("Please enter a search term.", "warning")
            return redirect(url_for('admin_dashboard'))

        # Try to determine if input is an ID (numeric) or name (text)
        if query.isdigit():  # Search by numeric ID
            students = Student.query.filter_by(student_id=int(query)).all()
            advisors = Advisor.query.filter_by(advisor_id=int(query)).all()
            admins = Administration.query.filter_by(id=int(query)).all()
        else:  # Search by name
            students = Student.query.filter(
                (Student.first_name.ilike(f"%{query}%")) | (Student.last_name.ilike(f"%{query}%"))
            ).all()

            advisors = Advisor.query.filter(
                (Advisor.first_name.ilike(f"%{query}%")) | (Advisor.last_name.ilike(f"%{query}%"))
            ).all()

            admins = Administration.query.filter(
                Administration.name.ilike(f"%{query}%")
            ).all()

        return render_template('admin_dashboard.html', students=students, advisors=advisors, admins=admins, query=query)





    