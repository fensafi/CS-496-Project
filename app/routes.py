from flask import render_template, request, redirect, url_for, flash, session
from .models import Student, Advisor, Administration
from . import db
from .models import Availability
from .models import Appointment
from flask_login import login_required, login_user, logout_user, LoginManager
from flask import Flask, request, jsonify  # Ensure jsonify is imported
import re
from datetime import datetime
from flask import session
import urllib.parse
from sqlalchemy import func
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from flask import Blueprint, session, jsonify
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
                session['student_email'] = user.email
                print("Student email stored in session:", session['student_email']) 
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
    
    @app.route('/api/session/student-email', methods=['GET'])
    def get_student_email():
        student_email = session.get('student_email')
        if student_email:
            return jsonify({'student_email': student_email})
        else:
            return jsonify({'error': 'Student email not found in session'}), 404
    
    @app.route('/schedule-appointments')
    def schedule_appointments():
        if session.get('user_type') == 'student':
            student = Student.query.filter_by(student_id=session.get('user_id')).first()
            if 'student_email' in session:
                print("Student email retrieved from session:", session['student_email'])  # Debugging
            else:
                print("Student email is MISSING from session!")  # Debugging
            return render_template('schedule-appointments.html', student=student, student_email=session.get('student_email'))
        return redirect(url_for('login'))

    @app.route('/advisors_availability')
    def advisors_availability():
        if session.get('user_type') == 'advisor':
            advsior = Advisor.query.filter_by(advisor_id=session.get('user_id')).first()
            return render_template('advisors_availability.html')
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
                datetime=selected_datetime  
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


    @app.route('/api/advisors', methods=['GET'])
    def get_advisors():
        advisors = Advisor.query.all()
        advisor_list = [
            {
                "id": advisor.id,
                "advisor_id": advisor.advisor_id,
                "first_name": advisor.first_name,
                "last_name": advisor.last_name,
                "email": advisor.email,
                "office": advisor.office
            }
            for advisor in advisors
        ]
        return jsonify(advisor_list)
    
    @app.route('/api/availability/<advisor_email>/dates', methods=['GET'])
    def get_advisor_availability(advisor_email):
        advisor_email = urllib.parse.unquote(advisor_email)
        print(f"Received advisor email: {advisor_email}")

        advisor = Advisor.query.filter_by(email=advisor_email).first()
        if not advisor:
            return jsonify({"error": "Advisor not found"}), 404

        available_dates = (
            db.session.query(func.date(Availability.datetime))
            .filter_by(advisor_email=advisor_email)
            .distinct()
            .all()
        )

        available_dates = [date[0].strftime('%Y-%m-%d') for date in available_dates]

        return jsonify({
            "first_name": advisor.first_name,
            "last_name": advisor.last_name,
            "email": advisor.email,
            "office": advisor.office,
            "available_dates": available_dates
        })


    @app.route('/api/availability/times/<advisor_email>/<date>', methods=['GET'])
    def get_available_times(advisor_email, date):
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            
            # Debugging output
            print(f"Fetching times for advisor: {advisor_email} on {date_obj}")

            availability = (
                db.session.query(Availability)
                .filter(Availability.advisor_email == advisor_email)
                .filter(func.date(Availability.datetime) == date_obj)
                .all()
            )

            print("Fetched availability:", availability)

            if not availability:
                return jsonify({"availableTimes": []})  # Return empty list if no availability

            available_times = [{"time": entry.datetime.strftime('%I:%M %p')} for entry in availability]

            return jsonify({"availableTimes": available_times})
        except Exception as e:
            print(f"Error fetching times: {str(e)}")
            return jsonify({"error": str(e)}), 500
        
        
    @app.route('/api/appointments', methods=['POST'])
    def schedule_appointment():
        data = request.get_json() 
        print("Received appointment data:", data)  # Log incoming data

        # Get values from request data
        student_email = data.get('student_email')
        advisor_email = data.get('advisor_email')
        advisor_name = data.get('advisor_name')
        advisor_last_name = data.get('advisor_last')
        advisor_office = data.get('advisor_office')
        datetime_str = data.get('datetime')
        student_note = data.get('note', '')

        # Check if all required fields are provided
        if not student_email or not advisor_email or not datetime_str:
            return jsonify({'error': 'Missing required fields'}), 400

        # Convert datetime string to datetime object
        try:
            appointment_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %I:%M %p')  # Adjust format as needed
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400

        # Get the student_id from student_email
        student = Student.query.filter_by(email=student_email).first()
        if not student:
            return jsonify({'error': 'Student not found'}), 400

        # Get the advisor_id from advisor_email
        advisor = Advisor.query.filter_by(email=advisor_email).first()
        if not advisor:
            return jsonify({'error': 'Advisor not found'}), 400

        # Create new Appointment record
        appointment = Appointment(
            student_id=student.student_id,  # Use the student_id from the Student record
            advisor_id=advisor.advisor_id,  # Use the advisor_id from the Advisor record
            student_email=student_email,
            advisor_email=advisor_email,
            advisor_name=advisor_name,
            advisor_last_name=advisor_last_name,
            advisor_office=advisor_office,
            datetime=appointment_datetime,
            note=student_note
        )

        # Add to database and commit
        try:
            db.session.add(appointment)
            db.session.commit()
            return jsonify({'success': True}), 200
        except Exception as e:
            db.session.rollback()
            print(f"Error saving appointment: {e}")
            return jsonify({'error': 'Error saving appointment'}), 500


    @app.route('/api/appointments', methods=['GET'])
    def get_appointments():
        student_email = session.get('student_email')  # Retrieve logged-in student's email
        if not student_email:
            return jsonify({"error": "User not logged in"}), 401

        # Get the current datetime
        current_time = datetime.now()

        # Fetch only upcoming appointments for the logged-in student
        appointments = Appointment.query.filter(
            Appointment.student_email == student_email,
            Appointment.datetime > current_time  # Filter out past appointments
        ).all()

        # Convert appointment objects to dictionary format for JSON response
        appointments_list = [
            {
                "id": appointment.id,  # Include ID for canceling
                "advisor_name": appointment.advisor_name,
                "advisor_last_name": appointment.advisor_last_name,
                "advisor_email": appointment.advisor_email,  # Include advisor's email
                "advisor_office": appointment.advisor_office,
                "datetime": appointment.datetime.strftime("%Y-%m-%d %H:%M"),
                "note": appointment.note
            }
            for appointment in appointments
        ]

        return jsonify(appointments_list)
    
    @app.route('/api/appointments/<int:appointment_id>', methods=['DELETE'])
    def delete_appointment(appointment_id):
        student_email = session.get('student_email')  # Ensure the student is logged in
        if not student_email:
            return jsonify({"error": "User not logged in"}), 401

        # Find the appointment by ID and student email
        appointment = Appointment.query.filter_by(id=appointment_id, student_email=student_email).first()

        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404

        # Delete the appointment
        db.session.delete(appointment)
        db.session.commit()

        return jsonify({"message": "Appointment canceled successfully!"})

    









    