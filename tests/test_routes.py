import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, session, url_for
from werkzeug.security import generate_password_hash
from flask_login import login_user
from app.models import Advisor, Student, Appointment, Availability, Note
from app.routes import init_routes
from datetime import datetime, timedelta
from app import db, create_app 

# Fixture to create a test Flask app
@pytest.fixture(scope='module')
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # Use in-memory DB for tests
        'WTF_CSRF_ENABLED': False
    })
    
    # Push application context and initialize DB
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

# Fixture to create a test client
@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

# Fixture to initialize database with test data
@pytest.fixture(scope='module')
def init_database(app):
    with app.app_context():
        student = Student(
            student_id=1,
            first_name="Test",
            last_name="Student",
            email="student@example.com",
            password=generate_password_hash("pass")
        )
        advisor = Advisor(
            advisor_id=1,
            first_name="Jane",
            last_name="Smith",
            email="advisor@example.com",
            password=generate_password_hash("pass"),
            office="Room 100"
        )
        db.session.add_all([student, advisor])
        db.session.commit()  # Make sure this is here

    yield  # Test execution happens here
    
    with app.app_context():
        db.drop_all()


# Tests successful users login 
def test_student_login_success(client, mocker):
    """Test successful student login"""
    response = client.post("/login", data={
        "email": "student@example.com",
        "password": "pass"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"student-dashboard" in response.data
    assert session['user_type'] == 'student'
    assert session['user_id'] == 1  # Assuming student ID is 1

def test_advisor_login_success(client):
    """Test successful advisor login"""
    response = client.post("/login", data={
        "email": "advisor@example.com",
        "password": "pass"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'advisor_dashboard' in response.data
    assert session['user_type'] == 'advisor'
    assert session['user_id'] == 1  # Assuming advisor ID is 1

def test_admin_login_success(client):
    """Test successful admin login"""
    response = client.post("/login", data={
        "email": "admin@example.com",
        "password": "pass"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'admin_dashboard' in response.data
    assert session['user_type'] == 'admin'

def test_invalid_login(client):
    """Test invalid login"""
    response = client.post("/login", data={
        "email": "invalid@example.com",
        "password": "wrongpass"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data  # Flash message


# Mocking db.session.commit and other db interactions in tests
@pytest.fixture
def mock_commit():
    with patch('app.db.session.commit') as mock_commit_func:
        yield mock_commit_func

# Tests that students dashboard is rendered correctly 
def test_student_dashboard(mocker, client, mock_commit):
    """Test that the student dashboard loads correctly"""
    # Making the GET request to the student dashboard page
    response = client.get('/student_dashboard')

    # Check the status code - should be 200 (OK)
    assert response.status_code == 200

    # Check if the "Student Dashboard" text is in the page
    assert b'Student Dashboard' in response.data

    # Check if the advisor's name (e.g., "Jane Smith") is in the page
    # This assumes that the advisor's name is present in the response
    assert b'Jane Smith' in response.data

    # Optionally, you can assert the student's email is being passed to the template
    # assert current_user.email.encode() in response.data


def test_get_advisors(client):
    """Test the /api/advisors endpoint"""
    response = client.get('/api/advisors')
    assert response.status_code == 200

    advisors = response.json
    assert len(advisors) == 1
    assert advisors[0]['first_name'] == "Jane"
    assert advisors[0]['last_name'] == "Smith"



def test_get_advisor_details(client):
    """Test the /api/advisors/1 endpoint"""
    response = client.get('/api/advisors/1')
    assert response.status_code == 200
    advisor = response.json
    assert advisor['name'] == "Jane Smith"
    assert advisor['email'] == "advisor@example.com"
    assert advisor['advisor_id'] == 1
    assert advisor['office'] == "Engineering Dept"



def test_get_availability_dates(client):
    """Test the /api/availability/<advisor_id>/dates endpoint"""
    advisor = Advisor.query.first()
    response = client.get(f'/api/availability/{advisor.advisor_id}/dates')
    assert response.status_code == 200
    data = response.json
    assert 'dates' in data
    assert isinstance(data['dates'], list)
    assert len(data['dates']) > 0  # Optional: remove if you're not seeding dates




def test_create_appointment(mocker, client, mock_commit):
    """Test creating an appointment"""
    # Ensure advisor and availability exist in the test DB
    advisor = Advisor.query.filter_by(advisor_id=1).first()
    if not advisor:
        advisor = Advisor(advisor_id=1, first_name="Jane", last_name="Smith", email="advisor@example.com", office="Room 101")
        db.session.add(advisor)
        db.session.commit()

    availability = Availability(
        advisor_id=1,
        date=datetime.strptime("2025-05-01", "%Y-%m-%d").date(),
        start_time=datetime.strptime("10:00 AM", "%I:%M %p").time(),
        end_time=datetime.strptime("10:15 AM", "%I:%M %p").time()
    )
    db.session.add(availability)
    db.session.commit()

    data = {
        "advisor_id": 1,
        "student_email": "student@example.com",
        "date": "2025-05-01",
        "time": "10:00 AM - 10:15 AM",
        "note": "Important discussion"
    }

    response = client.post('/api/appointments', json=data)
    assert response.status_code == 201
    assert "Appointment (and note) created successfully" in response.json['message']

    # Check if appointment was saved in the database
    appointment = Appointment.query.filter_by(student_id=1).first()
    assert appointment is not None
    assert appointment.date == datetime.strptime(data["date"], "%Y-%m-%d").date()
    assert appointment.start_time == datetime.strptime("10:00 AM", "%I:%M %p").time()
    assert appointment.end_time == datetime.strptime("10:15 AM", "%I:%M %p").time()

    # Check that note was saved
    note = Note.query.filter_by(appointment_id=appointment.appointment_id).first()
    assert note is not None
    assert note.content == "Important discussion"




def test_cancel_appointment(mocker, client, mock_commit):
    """Test canceling an appointment"""

    # Create an appointment to cancel
    appointment = Appointment(
        student_id=1,
        advisor_id=1,
        date=datetime.today().date(),
        start_time=datetime.now().time(),
        end_time=(datetime.now() + timedelta(minutes=30)).time()
    )
    db.session.add(appointment)
    db.session.commit()

    # Perform the POST request to cancel
    response = client.post(f'/cancel_appointment/{appointment.appointment_id}')

    # Assert the response and database state
    assert response.status_code == 302  # Redirect expected
    assert Appointment.query.get(appointment.appointment_id) is None  # Appointment should be deleted



def test_advisor_dashboard(client):
    """Test the advisor dashboard"""
    advisor = Advisor.query.first()

    # Properly set session variables inside client context
    with client.session_transaction() as sess:
        sess['user_type'] = 'advisor'
        sess['user_id'] = advisor.advisor_id

    response = client.get('/advisor_dashboard')
    assert response.status_code == 200
    assert b'Advisor Dashboard' in response.data
    assert bytes(advisor.first_name, 'utf-8') in response.data or bytes(advisor.last_name, 'utf-8') in response.data



def test_set_availability(client):
    """Test setting advisor availability"""
    advisor = Advisor.query.first()

    with client.session_transaction() as sess:
        sess['user_id'] = advisor.advisor_id  # Ensure session has advisor_id

    data = {
        'date': '2025-05-01',
        'start_time': '09:00',
        'end_time': '09:30'
    }
    response = client.post('/set_availability', data=data)

    assert response.status_code == 302  # Redirect to advisor_dashboard

    # Convert to date/time objects for DB query
    date_obj = datetime.strptime(data['date'], "%Y-%m-%d").date()
    start_time_obj = datetime.strptime(data['start_time'], "%H:%M").time()

    availability = Availability.query.filter_by(
        advisor_id=advisor.advisor_id,
        date=date_obj,
        start_time=start_time_obj
    ).first()

    assert availability is not None
    assert availability.end_time == (datetime.strptime('09:00', "%H:%M") + timedelta(minutes=15)).time()



def test_add_availabilities(client):
    """Test adding multiple availabilities"""
    advisor = Advisor.query.first()

    with client.session_transaction() as sess:
        sess['user_id'] = advisor.advisor_id
        sess['user_type'] = 'advisor'

    # Simulate login by patching `current_user` if using Flask-Login
    from flask_login import login_user
    login_user(advisor)

    data = {
        'start_date': '2025-05-01',
        'end_date': '2025-05-07',
        'start_time': '09:00',
        'end_time': '10:00',
        'days': ['0', '1', '2']  # Monday, Tuesday, Wednesday
    }

    response = client.post('/add_availabilities', data=data)
    assert response.status_code == 302  # Redirect to dashboard

    start_date = datetime.strptime(data['start_date'], "%Y-%m-%d").date()
    end_date = datetime.strptime(data['end_date'], "%Y-%m-%d").date()

    # Count number of slots added (for Mon, Tue, Wed across 7 days, each 09:00-10:00 → 4 slots/day)
    expected_days = {0, 1, 2}
    total_expected_slots = 0
    for i in range(7):
        date = start_date + timedelta(days=i)
        if date.weekday() in expected_days:
            total_expected_slots += 4  # 4 slots per hour

    availabilities = Availability.query.filter(
        Availability.advisor_id == advisor.advisor_id,
        Availability.date >= start_date,
        Availability.date <= end_date
    ).all()

    assert len(availabilities) == total_expected_slots


def test_delete_single_availability(client):
    """Test deleting a single availability slot"""
    # Create and commit a test availability
    availability = Availability(
        advisor_id=1,
        date=datetime(2025, 5, 2).date(),
        start_time=datetime.strptime("09:00", "%H:%M").time(),
        end_time=datetime.strptime("09:15", "%H:%M").time()
    )
    db.session.add(availability)
    db.session.commit()

    availability_id = availability.availability_id

    # Ensure it exists before deletion
    assert Availability.query.get(availability_id) is not None

    response = client.post(f'/delete_availability/{availability_id}')
    assert response.status_code == 302  # Redirect to advisor dashboard
    assert Availability.query.get(availability_id) is None  # Confirm it's deleted


def test_delete_multiple_availabilities(client):
    """Test deleting multiple availability slots within a date-time range"""
    advisor_id = 1
    date = datetime(2025, 5, 3).date()
    
    # Add 3 slots: 09:00–09:15, 09:15–09:30, 09:30–09:45
    times = ["09:00", "09:15", "09:30"]
    for t in times:
        start = datetime.strptime(t, "%H:%M")
        end = start + timedelta(minutes=15)
        slot = Availability(
            advisor_id=advisor_id,
            date=date,
            start_time=start.time(),
            end_time=end.time()
        )
        db.session.add(slot)

    db.session.commit()

    form_data = {
        "start_date": "2025-05-03",
        "end_date": "2025-05-03",
        "start_time": "09:00",
        "end_time": "09:45"
    }

    response = client.post('/delete_availabilities', data=form_data)
    assert response.status_code == 302  # Redirect to dashboard

    # Confirm all three slots are deleted
    remaining = Availability.query.filter_by(date=date).all()
    assert len(remaining) == 0



def test_add_note_as_advisor(client, mocker, mock_login):
    """Test advisor adding a note to an appointment"""
    # Simulate login for advisor
    mock_login(mocker)

    # Create an appointment
    appointment = Appointment(
        student_id=1,
        advisor_id=mocker.advisor_id,
        date=datetime.today().date(),
        start_time=datetime.now().time(),
        end_time=(datetime.now() + timedelta(minutes=30)).time()
    )
    db.session.add(appointment)
    db.session.commit()

    data = {
        'appointment_id': appointment.appointment_id,
        'note_content': 'Advisor test note'
    }

    response = client.post('/add_note', data=data)
    assert response.status_code == 302  # Should redirect to dashboard

    # Confirm note saved in DB
    note = Note.query.filter_by(appointment_id=appointment.appointment_id).first()
    assert note is not None
    assert note.content == 'Advisor test note'
    assert note.user_type == 'advisor'
    assert note.user_id == mocker.advisor_id


