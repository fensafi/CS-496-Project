import pytest
import os
from unittest.mock import patch, MagicMock
from flask import Flask, session, url_for
from werkzeug.security import generate_password_hash
from app import db, create_app
from app.models import Student, Advisor, Administration
from app.routes import init_routes


def test_student_login_success(client, mocker):
    """Test successful student login"""
    response = client.post("/login", data={
        "email": "student@wku.edu",
        "password": "password123"
    }, follow_redirects=True)
    
    assert response.status_code == 200

def test_advisor_login_success(client, mocker):
    """Test successful advisor login"""
    response = client.post("/login", data={
        "email": "advisor@wku.edu",
        "password": "password123"
    }, follow_redirects=True)
    
    assert response.status_code == 200


def test_admin_login_success(client, mocker):
    """Test successful admin login."""
    response = client.post("/login", data={
        "email": "admin@wku.edu",
        "password": "password123"
    }, follow_redirects=True)
    
    assert response.status_code == 200