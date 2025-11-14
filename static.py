# app.py
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


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.String(36), db.ForeignKey('application.id'), nullable=False, unique=True)
    amount = db.Column(db.Integer, nullable=False)
    method = db.Column(db.String(64), default='mock')
    status = db.Column(db.String(32), default='pending')
    paid_at = db.Column(db.DateTime)
    receipt_data = db.Column(db.Text)

    def __repr__(self):
        return f'<Payment {self.application_id} - {self.amount}>'


# -------------------------
# Utility validators
# -------------------------
def validate_bd_phone(form, field):
    val = field.data or ''
    digits = re.sub(r'\D', '', val)
    if not (len(digits) == 11 and digits.startswith('01')):
        raise ValidationError('Enter a valid Bangladeshi phone number (11 digits, starts with 01).')


def validate_password_strength(form, field):
    val = field.data or ''
    if (len(val) < 8 or not re.search(r'[A-Z]', val) or not re.search(r'[a-z]', val)
            or not re.search(r'[0-9]', val) or not re.search(r'[!@#$%^&*]', val)):
        raise ValidationError('Password must be 8+ chars with upper, lower, digit & special char.')


def validate_dob_age(form, field):
    dob = field.data
    if not dob:
        raise ValidationError('Date of birth is required.')
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    if age < 15:
        raise ValidationError('Applicant must be at least 15 years old.')


def allowed_file(filename):
    if not filename:
        return False
    ext = filename.rsplit('.', 1)[-1].lower()
    return ext in ALLOWED_EXT


class ApplicationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=200)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=200)])
    phone = StringField('Phone', validators=[DataRequired(), validate_bd_phone])
    guardian = StringField('Guardian', validators=[Optional(), Length(max=200)])
    address = TextAreaField('Address', validators=[Optional(), Length(max=1000)])
    education = StringField('Education', validators=[Optional(), Length(max=300)])
    exam_roll = StringField('Exam Roll', validators=[Optional(), Length(max=100)])
    department = SelectField('Department', coerce=int, validators=[DataRequired()])
    program = SelectField('Program', choices=[('bachelors', 'Bachelors'), ('masters', 'Masters'), ('postgraduate', 'Postgraduate')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), validate_password_strength])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    dob = DateField('Date of Birth', validators=[DataRequired(), validate_dob_age], format='%Y-%m-%d')
    photo = FileField('Photo (jpg/png)', validators=[Optional()])
    sign = FileField('Signature (jpg/png)', validators=[Optional()])
    transcript = FileField('Transcript (pdf/jpg)', validators=[Optional()])
    submit = SubmitField('Submit Application')


class PaymentForm(FlaskForm):
    method = SelectField('Method', choices=[('bkash', 'Bkash'), ('nagad', 'Nagad'), ('card', 'Card'), ('mock', 'Mock')], validators=[DataRequired()])
    submit = SubmitField('Pay')


# -------------------------
# Simple templates (inline)
# -------------------------
BASE_HTML = """
<!doctype html>
<title>UAP Admission</title>
<link rel="stylesheet" href="https://cdn.simplecss.org/simple.min.css">
<div class="container">
  <header><h1>UAP Admission Portal</h1></header>
  <main>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <ul>
        {% for cat, msg in messages %}
          <li style="color: {% if cat=='error' %}red{% else %}green{% endif %}">{{ msg }}</li>
        {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}
    {% block content %}{% endblock %}
  </main>
  <footer><p>&copy; UAP Admission Demo</p></footer>
</div>
"""

INDEX_HTML = """
{% extends base %}
{% block content %}
  <p><a href="{{ url_for('apply') }}">Apply Now</a> | <a href="{{ url_for('admin_list') }}">Admin: View Applications</a></p>
  <p>Sample Departments:</p>
  <ul>
  {% for d in depts %}
    <li>{{ d.code }} - {{ d.name }} (fee: {{ d.calculate_fee() }})</li>
  {% endfor %}
  </ul>
{% endblock %}
"""

APPLY_HTML = """
{% extends base %}
{% block content %}
  <h2>Application Form</h2>
  <form method="post" enctype="multipart/form-data">
    {{ form.hidden_tag() }}
    <label>{{ form.full_name.label }} {{ form.full_name(class_="input") }}</label>
    <label>{{ form.email.label }} {{ form.email(class_="input") }}</label>
    <label>{{ form.phone.label }} {{ form.phone(class_="input") }}</label>
    <label>{{ form.guardian.label }} {{ form.guardian(class_="input") }}</label>
    <label>{{ form.address.label }} {{ form.address(rows=3) }}</label>
    <label>{{ form.education.label }} {{ form.education(class_="input") }}</label>
    <label>{{ form.exam_roll.label }} {{ form.exam_roll(class_="input") }}</label>
    <label>{{ form.department.label }} {{ form.department() }}</label>
    <label>{{ form.program.label }} {{ form.program() }}</label>
    <label>{{ form.dob.label }} {{ form.dob() }}</label>
    <label>{{ form.password.label }} {{ form.password() }}</label>
    <label>{{ form.confirm_password.label }} {{ form.confirm_password() }}</label>
    <label>{{ form.photo.label }} {{ form.photo() }}</label>
    <label>{{ form.sign.label }} {{ form.sign() }}</label>
    <label>{{ form.transcript.label }} {{ form.transcript() }}</label>
    <p>{{ form.submit() }}</p>
  </form>
{% endblock %}
"""

APPLICATION_VIEW_HTML = """
{% extends base %}
{% block content %}
  <h2>Application {{ app.id }}</h2>
  <p><strong>Name:</strong> {{ app.full_name }}</p>
  <p><strong>Email:</strong> {{ app.email }}</p>
  <p><strong>Phone:</strong> {{ app.phone }}</p>
  <p><strong>Department:</strong> {{ app.department.code }} - {{ app.department.name }}</p>
  <p><strong>Program:</strong> {{ app.program }}</p>
  <p><strong>Status:</strong> {{ app.status }}</p>
  <p><strong>Applied at:</strong> {{ app.applied_at }}</p>

  <h3>Files</h3>
  <ul>
  {% for f in app.files %}
    <li><a href="{{ url_for('uploaded_file', filename=f.filename) }}">{{ f.kind }} - {{ f.filename }}</a></li>
  {% endfor %}
  </ul>

  {% if not app.payment %}
    <h3>Make Payment (mock)</h3>
    <form method="post" action="{{ url_for('pay', app_id=app.id) }}">
      {{ pay_form.hidden_tag() }}
      {{ pay_form.method() }}
      {{ pay_form.submit() }}
    </form>
  {% else %}
    <h3>Payment</h3>
    <p>Amount: {{ app.payment.amount }}</p>
    <p>Status: {{ app.payment.status }}</p>
  {% endif %}

  <p><a href="{{ url_for('admin_list') }}">Back to list</a></p>
{% endblock %}
"""

ADMIN_LIST_HTML = """
{% extends base %}
{% block content %}
  <h2>All Applications</h2>
  <table>
    <thead><tr><th>ID</th><th>Name</th><th>Dept</th><th>Status</th><th>Actions</th></tr></thead>
    <tbody>
    {% for a in apps %}
      <tr>
        <td>{{ a.id }}</td>
        <td>{{ a.full_name }}</td>
        <td>{{ a.department.code }}</td>
        <td>{{ a.status }}</td>
        <td>
          <a href="{{ url_for('view_application', app_id=a.id) }}">View</a> |
          <a href="{{ url_for('set_status', app_id=a.id, new_status='under_review') }}">Mark Review</a> |
          <a href="{{ url_for('set_status', app_id=a.id, new_status='approved') }}">Approve</a> |
          <a href="{{ url_for('set_status', app_id=a.id, new_status='rejected') }}">Reject</a>
        </td>
      </tr>
    {% endfor %}
    </tbody>
  </table>
  <p><a href="{{ url_for('index') }}">Home</a></p>
{% endblock %}
"""

# -------------------------
# Routes
# -------------------------
@app.route('/')
def index():
    depts = Department.query.all()
    return render_template_string(INDEX_HTML, base=BASE_HTML, depts=depts)


@app.route('/apply', methods=['GET', 'POST'])
def apply():
    form = ApplicationForm()
    # populate departments choices
    depts = Department.query.all()
    form.department.choices = [(d.id, f'{d.code} - {d.name}') for d in depts]
    if request.method == 'POST' and form.validate_on_submit():
        # create application
        dept = Department.query.get(form.department.data)
        if not dept:
            flash('Selected department not found', 'error')
            return redirect(url_for('apply'))

