import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, session, url_for
from werkzeug.security import generate_password_hash
from app import db
from app.models import Student, Advisor, Administration
from app.routes import init_routes

# fixture to create a test flask app
@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    init_routes(app)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

# fixture for the client
@pytest.fixture
def client(app):
    return app.test_client()

# test cases

def test_student_login_success(client, mocker):
    """Test successful student login"""
    mock_student = Student(
        student_id=1,
        email="student@wku.edu",
        password=generate_password_hash("password123")
    )
    mocker.patch(
        "app.routes.Student.query.filter_by",
        return_value=MagicMock(first=MagicMock(return_value=mock_student))
    )
    response = client.post("/login", data={
        "email": "student@wku.edu",
        "password": "password123"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"student-dashboard" in response.data
    assert session.get("user_type") == "student"

def test_advisor_login_success(client, mocker):
    """Test successful advisor login"""
    mock_advisor = Advisor(
        advisor_id=1,
        email="advisor@wku.edu",
        password=generate_password_hash("password123")
    )
    mocker.patch(
        "app.routes.Advisor.query.filter_by",
        return_value=MagicMock(first=MagicMock(return_value=mock_advisor))
    )
    response = client.post("/login", data={
        "email": "advisor@wku.edu",
        "password": "password123"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"advisor-dashboard" in response.data
    assert session.get("user_type") == "advisor"

def test_admin_login_success(client, mocker):
    """Test successful admin login."""
    mock_admin = Administration(
        admin_id=1,
        email="admin@wku.edu",
        password=generate_password_hash("password123")
    )
    mocker.patch(
        "app.routes.Administration.query.filter_by",
        return_value=MagicMock(first=MagicMock(return_value=mock_admin))
    )
    
    response = client.post("/login", data={
        "email": "admin@wku.edu",
        "password": "password123"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"admin-dashboard" in response.data
    assert session.get("user_type") == "admin"