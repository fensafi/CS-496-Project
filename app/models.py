from . import db

from werkzeug.security import generate_password_hash, check_password_hash

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Use db.String for password
    
    advisor = db.relationship('Advisor', backref='students', lazy=True)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)  # Hash password before saving
    
    def check_password(self, password):
        return check_password_hash(self.password, password)  # Check if passwords match

    def __repr__(self):
        return f'<Student {self.name}>'

class Advisor(db.Model):
    __tablename__ = 'advisors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Use db.String for password
    office = db.Column(db.String(100), nullable=False)  # Assuming office is a string
    
    def set_password(self, password):
        self.password = generate_password_hash(password)  # Hash password before saving
    
    def check_password(self, password):
        return check_password_hash(self.password, password)  # Check if passwords match

    def __repr__(self):
        return f'<Advisor {self.name}>'

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    advisor_id = db.Column(db.Integer, db.ForeignKey('advisors.id'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    
    student = db.relationship('Student', backref='appointments', lazy=True)
    advisor = db.relationship('Advisor', backref='appointments', lazy=True)
    
    def __repr__(self):
        return f'<Appointment {self.id} - {self.datetime}>'

class Administration(db.Model):
    __tablename__ = 'administration'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Use db.String for password
    
    def set_password(self, password):
        self.password = generate_password_hash(password)  # Hash password before saving
    
    def check_password(self, password):
        return check_password_hash(self.password, password)  # Check if passwords match

    def __repr__(self):
        return f'<Administration {self.name}>'
