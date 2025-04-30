import pytest
import os
from unittest.mock import patch, MagicMock
from flask import Flask, session, url_for
from werkzeug.security import generate_password_hash
from app import db, create_app
from app.models import Student, Advisor, Administration
from app.routes import init_routes

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

@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

@pytest.fixture(scope='module')
def init_database(app):
    # Add test data
    with app.app_context():
        student = Student(email="student@wku.edu", password="password123")
        advisor = Advisor(email="advisor@wku.edu", password="password123")
        admin = Administration(email="admin@wku.edu", password="password123")
        
        db.session.add(student)
        db.session.add(advisor)
        db.session.add(admin)
        db.session.commit()
    
    yield  # Testing happens here
    
    with app.app_context():
        db.drop_all()

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