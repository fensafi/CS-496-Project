from . import db
from werkzeug.security import generate_password_hash, check_password_hash
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
    student_id = db.Column(db.BigInteger, db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    advisor_id = db.Column(db.BigInteger, db.ForeignKey('advisors.advisor_id', ondelete='CASCADE'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)

    student = db.relationship('Student', backref='appointments', lazy=True)
    advisor = db.relationship('Advisor', backref='appointments', lazy=True)



    def to_dict(self):
        return {
            "studentId": self.student_id,
            "advisorId": self.advisor_id,
            "studentName": f"{self.student.first_name} {self.student.last_name}",
            "advisorName": f"{self.advisor.first_name} {self.advisor.last_name}",
            "date": self.datetime,
        }

class Availability(db.Model):
    __tablename__ = 'availabilities'
    availability_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    advisor_id = db.Column(db.BigInteger, db.ForeignKey('advisors.advisor_id'), primary_key=True, nullable=False)  # ForeignKey to Advisor's id
    datetime = db.Column(db.DateTime, nullable=False)

    advisor = db.relationship('Advisor', backref='availabilities', lazy=True)
