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
