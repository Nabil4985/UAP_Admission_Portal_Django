import os
import re
import uuid
from datetime import datetime, date
from flask import (Flask, render_template_string, request, redirect,
                   url_for, flash, send_from_directory, abort, jsonify)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, SelectField, PasswordField,
                     DateField, TextAreaField, IntegerField, FileField)
from wtforms.validators import (DataRequired, Email, Length, Regexp,
                                EqualTo, ValidationError, Optional)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# -------------------------
# Configuration
# -------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXT = {'jpg', 'jpeg', 'png', 'pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-me'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'uap_admission.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB global limit

db = SQLAlchemy(app)

# -------------------------
# Models
# -------------------------
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    total_credits = db.Column(db.Integer, default=0)
    per_credit_fee = db.Column(db.Integer, default=0)
    seats = db.Column(db.Integer, default=0)

    def calculate_fee(self):
        return (self.total_credits or 0) * (self.per_credit_fee or 0)

    def __repr__(self):
        return f'<Dept {self.code}>'

class Application(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(32), nullable=False)
    guardian = db.Column(db.String(200))
    address = db.Column(db.Text)
    education = db.Column(db.String(300))
    exam_roll = db.Column(db.String(100))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    program = db.Column(db.String(50), nullable=False)
    fee_amount = db.Column(db.Integer, default=0)
    status = db.Column(db.String(32), default='submitted')
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    receipt_text = db.Column(db.Text)
    password_hash = db.Column(db.String(200))

    department = db.relationship('Department', backref='applications')
    files = db.relationship('ApplicationFile', backref='application', cascade='all, delete-orphan', lazy=True)
    payment = db.relationship('Payment', backref='application', uselist=False, cascade='all, delete-orphan')

    

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash or '', raw)

    def __repr__(self):
        return f'<App {self.id} - {self.full_name}>'


class ApplicationFile(db.Model):
  
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.String(36), db.ForeignKey('application.id'), nullable=False)
    kind = db.Column(db.String(32), nullable=False)
    filename = db.Column(db.String(300), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def filepath(self):
        return os.path.join(app.config['UPLOAD_FOLDER'], self.filename)

    def __repr__(self):
        return f'<File {self.filename}>'
