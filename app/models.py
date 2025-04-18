from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin

class Student(UserMixin, db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.BigInteger, primary_key=True, nullable=False)  # 9-digit numeric ID as PK
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return str(self.student_id)  # Make sure get_id() returns the correct value


class Advisor(UserMixin, db.Model):
    __tablename__ = 'advisors'
    advisor_id = db.Column(db.BigInteger, primary_key=True, nullable=False)  # Advisor ID as PK
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    office = db.Column(db.String(100), nullable=False)

    availabilities = db.relationship('Availability', backref='advisor_relation', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return str(self.advisor_id)  # Make sure get_id() returns the correct value


class Administration(UserMixin, db.Model):
    __tablename__ = 'administration'
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return str(self.admin_id)


class Appointment(db.Model):
    __tablename__ = 'appointments'
    appointment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.BigInteger, db.ForeignKey('students.student_id'), nullable=False)
    advisor_id = db.Column(db.BigInteger, db.ForeignKey('advisors.advisor_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='pending')
    
    student = db.relationship('Student', backref='appointments', lazy=True)
    advisor = db.relationship('Advisor', backref='appointments', lazy=True)
    notes = db.relationship('Note', backref='appointment', lazy=True, cascade="all, delete-orphan")


class Note(db.Model):
    __tablename__ = 'notes'
    note_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.appointment_id'), nullable=False)
    user_id = db.Column(db.BigInteger, nullable=False)  # ID of the user (either student or advisor)
    user_type = db.Column(db.String(10), nullable=False)  # 'student' or 'advisor'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Availability(db.Model):
    __tablename__ = 'availabilities'
    availability_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    advisor_id = db.Column(db.BigInteger, db.ForeignKey('advisors.advisor_id', ondelete='CASCADE'), nullable=False)  # ForeignKey to Advisor's id
    date = db.Column(db.Date, nullable=False)  
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)


