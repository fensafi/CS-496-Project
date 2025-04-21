from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from .models import Student, Advisor, Administration, Appointment, Availability, Note
from . import db
from .models import Availability
from flask_login import login_required, login_user, logout_user, LoginManager
from flask import Flask, request, jsonify  
import re
from datetime import datetime, timedelta
from flask import session
from flask_login import current_user
from collections import defaultdict
from app.email import send_appointment_confirmation
from flask_mail import Mail, Message
from app import mail
from itsdangerous import URLSafeTimedSerializer
from flask_babel import _





main = Blueprint('main', __name__)
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
    def index():
        return render_template('home.html', title=_("Home"))
    
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

    @app.route('/change_password', methods=['GET', 'POST'])
    @login_required
    def change_password():
        if request.method == 'POST':
            current_pwd = request.form['current_password']
            new_pwd = request.form['new_password']
            confirm_pwd = request.form['confirm_password']

            if new_pwd != confirm_pwd:
                flash('New passwords do not match.', 'danger')
                return redirect(url_for('change_password'))

            if not current_user.check_password(current_pwd):
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('change_password'))

            current_user.set_password(new_pwd)
            db.session.commit()
            flash('Password changed successfully.', 'success')
            return redirect(url_for('home'))

        return render_template('change-password.html')

    @app.route('/forgot_password', methods=['GET', 'POST'])
    def forgot_password():
        if request.method == 'POST':
            email = request.form['email']
            
            # Check if the email exists in any of the tables (Students, Advisors, Administration)
            student = Student.query.filter_by(email=email).first()
            advisor = Advisor.query.filter_by(email=email).first()
            admin = Administration.query.filter_by(email=email).first()

            # If no user is found, flash an error message
            if not student and not advisor and not admin:
                flash('No account associated with this email address.', 'danger')
                return redirect(url_for('forgot_password'))

            user = None
            if student:
                user = student
            elif advisor:
                user = advisor
            elif admin:
                user = admin
            # Here, you would send the reset email (same logic as before)
            # For simplicity, let's assume sending the reset email is done by a function
            s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            token = s.dumps(user.email, salt='password-reset-salt')
            reset_url = url_for('reset_password', token=token, _external=True)
            
            msg = Message(
                'Password Reset Request',
                recipients=[user.email],
                body=f'Click the link to reset your password: {reset_url}'
            )
            mail.send(msg)
            flash('Password reset link has been sent to your email.', 'info')
            return redirect(url_for('login'))

        return render_template('forgot-password.html')

    @app.route('/reset_password/<token>', methods=['GET', 'POST'])
    def reset_password(token):
        user = User.verify_reset_token(token)
        if not user:
            flash('Invalid or expired token', 'danger')
            return redirect(url_for('forgot_password'))

        if request.method == 'POST':
            new_password = request.form['new_password']
            confirm = request.form['confirm_password']
            if new_password != confirm:
                flash('Passwords do not match', 'danger')
                return redirect(request.url)

            user.set_password(new_password)
            db.session.commit()
            flash('Your password has been updated.', 'success')
            return redirect(url_for('login'))

        return render_template('reset-password.html')



    ''' Student Dashboard'''


    @app.route('/student_dashboard')
    @login_required  # Ensure user is logged in
    def student_dashboard():
        if current_user.is_authenticated:
            advisors = Advisor.query.all()  # Get all advisors
            return render_template('student-dashboard.html', advisors=advisors, student_email=current_user.email)
        else:
            return redirect(url_for('login'))

    # Route for fetching advisor details
    @app.route('/api/advisors')
    def get_advisors():
        advisors = Advisor.query.all()
        advisor_data = []
        for advisor in advisors:
            advisor_data.append({
                'advisor_id': advisor.advisor_id,
                'first_name': advisor.first_name,
                'last_name': advisor.last_name,
                'department': advisor.office  # Assuming department information is stored in 'office'
            })
        return jsonify(advisor_data)

    # Route for fetching advisor details by name
    @app.route('/api/advisors/<advisor_id>')
    def get_advisor_details(advisor_id):
        advisor = Advisor.query.filter_by(advisor_id=advisor_id).first()
        if advisor:
            return jsonify({
                'name': f"{advisor.first_name} {advisor.last_name}",
                'advisor_id': advisor.advisor_id,
                'email': advisor.email,
                'office': advisor.office
            })
        else:
            return jsonify({'error': 'Advisor not found'}), 404

    # Route for fetching availability dates for a specific advisor
    @app.route('/api/availability/<advisor_id>/dates')
    def get_availability_dates(advisor_id):
        advisor = Advisor.query.filter_by(advisor_id=advisor_id).first()
        
        if advisor:
            availabilities = Availability.query.filter_by(advisor_id=advisor.advisor_id).all()
            available_dates = sorted(set([a.date for a in availabilities]))  # Get unique available dates
            return jsonify({'dates': available_dates})
        else:
            return jsonify({'error': 'Advisor not found'}), 404

    @app.route('/api/availability/times/<selected_date>')
    def get_available_times(selected_date):
        try:
            parsed_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400

        available_times = Availability.query.filter_by(date=parsed_date).all()

        formatted_slots = [
            f"{a.start_time.strftime('%I:%M %p')} - {a.end_time.strftime('%I:%M %p')}"
            for a in available_times
        ]

        return jsonify({'availableTimes': formatted_slots})

    @app.route('/api/availabilities/summary')
    def get_all_availability_summary():
        availabilities = Availability.query.all()
        day_counts = defaultdict(int)

        for a in availabilities:
            day_counts[a.date] += 1

        events = [{
            'title': f"{count} availabilities",
            'start': date.isoformat(),
            'allDay': True
        } for date, count in day_counts.items()]

        return jsonify(events)

    # Creates appointment from student only 
    @app.route('/api/appointments', methods=['POST'])
    @login_required
    def api_create_appointment():
        data = request.get_json()

        # Extract data from the request body
        advisor_name = data.get("advisor_name")
        advisor_id = data.get("advisor_id")
        student_email = data.get("student_email")
        date_str = data.get("date")
        time_str = data.get("time")
        note_text = data.get("note")

        # Convert date_str to a datetime object
        try:
            appointment_date = datetime.strptime(date_str, "%Y-%m-%d")  # assuming date format like '2025-04-05'
        except ValueError:
            return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD."}), 400

        # Split time_str into start_time and end_time (assuming format like '12:24 AM - 12:27 AM')
        try:
            time_parts = time_str.split(" - ")
            start_time_str = time_parts[0]
            end_time_str = time_parts[1]
            
            # Convert start and end times to datetime objects (you can adjust format as needed)
            start_time = datetime.strptime(start_time_str, "%I:%M %p")  # Assuming format like '12:24 AM'
            end_time = datetime.strptime(end_time_str, "%I:%M %p")  # Assuming format like '12:27 AM'
        except (ValueError, IndexError):
            return jsonify({"error": "Invalid time format. Expected format 'hh:mm AM/PM - hh:mm AM/PM.'"}), 400

        # Fetch advisor using the advisor_name (assuming a lookup by name)
        advisor = Advisor.query.filter_by(advisor_id=advisor_id).first()

        if not advisor:
            return jsonify({"error": "Advisor not found."}), 404

        # Assuming you already have the current_user object that provides the student ID
        appointment = Appointment(
            student_id=current_user.student_id,
            advisor_id=advisor.advisor_id,
            date=appointment_date,
            start_time=start_time,
            end_time=end_time,
        )

        # Save appointment
        db.session.add(appointment)
        db.session.commit()

        # Send confirmation email to student and advisor
        msg = Message(
            'Appointment Confirmation',
            recipients=[current_user.email, advisor.email],
            body=f'An appointment has been scheduled for {appointment_date}'
        )
        mail.send(msg)

        # Now, delete the availability for that time slot (assuming it's already in the Availability model)
        availability = Availability.query.filter_by(advisor_id=advisor.advisor_id, date=appointment_date, 
                                                    start_time=start_time.time(), end_time=end_time.time()).first()

        if availability:
            db.session.delete(availability)
            db.session.commit()

        # Save note if provided
        if note_text and note_text.strip():
            new_note = Note(
                appointment_id = appointment.appointment_id,
                user_id = current_user.student_id,
                user_type = 'student',
                content = note_text,
            )
            db.session.add(new_note)
            db.session.commit()

        return jsonify({"message": "Appointment (and note) created successfully"}), 201


    @app.route('/api/availabilities/summary/<int:advisor_id>')
    def get_advisor_availability_summary(advisor_id):
        availabilities = Availability.query.filter_by(advisor_id=advisor_id).all()
        day_counts = defaultdict(int)

        for a in availabilities:
            day_counts[a.date] += 1

        events = [{
            'title': f"{count} availabilities",
            'start': date.isoformat(),
            'allDay': True
        } for date, count in day_counts.items()]

        return jsonify(events)

    @app.route('/scheduled-appointments')
    @login_required
    def scheduled_appointments():
        if not hasattr(current_user, 'student_id'):
            return redirect(url_for('home'))  # Prevent access if not a student

        appointments = (
            db.session.query(Appointment, Advisor)
            .join(Advisor, Appointment.advisor_id == Advisor.advisor_id)
            .filter(Appointment.student_id == current_user.student_id)
            .order_by(Appointment.date, Appointment.start_time)
            .all()
        )

        return render_template('scheduled-appointments.html', appointments=appointments)



    ''' Advisor Dashboard'''


    @app.route('/advisor_dashboard')
    def advisor_dashboard():
        if session.get('user_type') == 'advisor':
            advisor = Advisor.query.filter_by(advisor_id=session.get('user_id')).first()
            
            # Get the week requested by the user (default to the current week)
            requested_week = request.args.get('week', None)
            
            # Get today's date and calculate the start of the current week (Monday)
            today = datetime.today()
            if requested_week:
                start_of_week = datetime.strptime(requested_week, "%Y-%m-%d")
            else:
                start_of_week = today - timedelta(days=today.weekday())  # Monday of current week

            end_of_week = start_of_week + timedelta(days=6)  # Sunday of the same week

            # Filter appointments for the selected week
            appointments = Appointment.query.filter(
                Appointment.advisor_id == advisor.advisor_id,
                Appointment.date >= start_of_week.date(),
                Appointment.date <= end_of_week.date()
            ).order_by(Appointment.date, Appointment.start_time).all()

             # 👉 Aggregate notes for each appointment
            for appointment in appointments:
                note_lines = []
                for note in appointment.notes:
                    line = f"{note.user_type.capitalize()}: {note.content}"
                    note_lines.append(line)
                appointment.aggregated_notes = "\n".join(note_lines)


            availabilities = Availability.query.filter(
                Availability.advisor_id == advisor.advisor_id,  
                Availability.date >= start_of_week.date(),
                Availability.date <= end_of_week.date()
            ).order_by(Availability.date, Availability.start_time).all()

            return render_template('advisor-dashboard.html', 
                                    appointments=appointments,
                                    availabilities=availabilities,  
                                    start_of_week=start_of_week.date(),
                                    end_of_week=end_of_week.date())

        return redirect(url_for('login'))

    @app.route("/set_availability", methods=["POST"])
    def set_availability():
        try:
            selected_date = request.form.get("date")
            start_time = request.form.get("start_time")
            end_time = request.form.get("end_time")
            advisor_id = session.get("user_id")

            if not all([selected_date, start_time, end_time, advisor_id]):
                return jsonify({"message": "Missing required fields"}), 400

            formatted_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
            formatted_start = datetime.strptime(start_time, "%H:%M")
            formatted_end = datetime.strptime(end_time, "%H:%M")

            current = formatted_start
            while current < formatted_end:
                slot_start = current
                slot_end = current + timedelta(minutes=15)

                availability = Availability(
                    advisor_id=advisor_id,
                    date=formatted_date,
                    start_time=slot_start.time(),
                    end_time=slot_end.time()  # ⬅️ Add this to satisfy NOT NULL constraint
                )

                db.session.add(availability)
                current += timedelta(minutes=15)

            db.session.commit()

            print(f"Saved 15-minute slots from {formatted_start.time()} to {formatted_end.time()} on {formatted_date}")

        except Exception as e:
            db.session.rollback()
            print(f"Error: {str(e)}")
            return jsonify({"message": "Error while adding availability."}), 500

        return redirect(url_for('advisor_dashboard'))


    @app.route('/delete_availability/<int:availability_id>', methods=['POST'])
    def delete_availability(availability_id):
        availability = Availability.query.get(availability_id)
        
        if availability:
            db.session.delete(availability)
            db.session.commit()
            print(f"DELETE route hit with ID: {availability_id}")
        
        # After deletion, redirect to the advisor dashboard or any other page you want
        return redirect(url_for('advisor_dashboard'))


    @app.route('/advisor_dashboard/cancel/<int:appointment_id>', methods=['POST'])
    @login_required
    def cancel_appointment(appointment_id):
        appointment = Appointment.query.get(appointment_id)
        
        if appointment:
            try:
                db.session.delete(appointment)
                db.session.commit()
                flash('Appointment deleted successfully!', 'success')

            except Exception as e:
                db.session.rollback()
                flash(f'Error deleting appointment: {str(e)}', 'danger')
        else:
            flash('Appointment not found!', 'danger')

        return redirect(url_for('advisor_dashboard'))


    @app.route('/add_note', methods=['POST'])
    @login_required
    def add_note():
        appointment_id = request.form.get('appointment_id')
        note_content = request.form.get('note_content')

        # Validate form inputs
        if not appointment_id or not note_content:
            flash("Missing information", "danger")
            return redirect(url_for('advisor_dashboard'))

        # Ensure user is authenticated (redundant with @login_required, but kept for clarity)
        if not current_user.is_authenticated:
            flash("You must be logged in to add a note.", "danger")
            return redirect(url_for('login'))

        # Retrieve appointment
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            flash("Appointment not found", "danger")
            return redirect(url_for('advisor_dashboard'))

        # Determine user type and ID
        is_advisor = hasattr(current_user, 'advisor_id')
        user_id = current_user.advisor_id if is_advisor else current_user.student_id
        user_type = "advisor" if is_advisor else "student"

        # Create the note
        new_note = Note(
            appointment_id=appointment_id,
            user_id=user_id,
            user_type=user_type,
            content=note_content
        )

        # Save to the database
        db.session.add(new_note)
        db.session.commit()

        flash("Note added successfully!", "success")
        return redirect(url_for('advisor_dashboard'))



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

        return render_template('admin-dashboard.html', students=students, advisors=advisors, admins=admins)
    
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
            user = Administration.query.filter_by(admin_id=user_id).first()
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

        return render_template('admin-dashboard.html', students=students, advisors=advisors, admins=admins, query=query)





    