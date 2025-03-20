from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Student(UserMixin, db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)  # Internal DB ID
    student_id = db.Column(db.BigInteger, unique=True, nullable=False)  # 9-digit numeric ID
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return str(self.id)

class Advisor(UserMixin, db.Model):
    __tablename__ = 'advisors'
    id = db.Column(db.Integer, primary_key=True)  # Internal DB ID
    advisor_id = db.Column(db.BigInteger, unique=True, nullable=False)  # Advisor ID
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    office = db.Column(db.String(100), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return str(self.id)

class Administration(UserMixin, db.Model):
    __tablename__ = 'administration'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return str(self.id)

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.BigInteger, db.ForeignKey('students.student_id'), nullable=False)
    advisor_id = db.Column(db.BigInteger, db.ForeignKey('advisors.advisor_id'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    
    student = db.relationship('Student', backref='appointments', lazy=True, primaryjoin="Student.student_id == Appointment.student_id")
    advisor = db.relationship('Advisor', backref='appointments', lazy=True, primaryjoin="Advisor.advisor_id == Appointment.advisor_id")


