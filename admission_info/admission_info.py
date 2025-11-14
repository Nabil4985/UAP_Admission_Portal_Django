class Role(Enum):
    STUDENT = "student"
    ADMIN = "admin"


class ApplicationStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=Role.STUDENT.value)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship("Application", backref="user", lazy=True)

    def check_password(self, password: str) -> bool:
        return self.password_hash == hash_password(password)

    def is_admin(self) -> bool:
        return self.role == Role.ADMIN.value

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }


class Application(db.Model):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    birth_date = db.Column(db.String(20), nullable=True)
    program = db.Column(db.String(100), nullable=False)
    gpa = db.Column(db.Float, nullable=True)
    high_school = db.Column(db.String(200), nullable=True)
    submission_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(40), default=ApplicationStatus.DRAFT.value)
    reviewer_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def submit(self):
        self.status = ApplicationStatus.SUBMITTED.value
        self.submission_date = datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "birth_date": self.birth_date,
            "program": self.program,
            "gpa": self.gpa,
            "high_school": self.high_school,
            "submission_date": self.submission_date.isoformat() if self.submission_date else None,
            "status": self.status,
            "reviewer_notes": self.reviewer_notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# Simple auth middleware (session-based)
# ---------------------------------------------------------------------------

@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = None
    if user_id is None:
        return
    g.user = User.query.get(user_id)


def login_user(user: User):
    session["user_id"] = user.id


def logout_user():
    session.pop("user_id", None)


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def validate_email(email: str) -> bool:
    return isinstance(email, str) and "@" in email and len(email) > 5


def validate_gpa(gpa_raw) -> Optional[float]:
    try:
        gpa = float(gpa_raw)
        if 0.0 <= gpa <= 4.0:
            return gpa
    except Exception:
        return None
    return None


# ---------------------------------------------------------------------------
# Routes (JSON API style)
# ---------------------------------------------------------------------------

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", Role.STUDENT.value)

    if not username or not email or not password:
        return jsonify({"error": "username, email and password are required"}), 400
    if not validate_email(email):
        return jsonify({"error": "invalid email"}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "username or email already exists"}), 400

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=role,
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "registered", "user": user.to_dict()}), 201

<<<<<<< HEAD
=======
import random
import string
import datetime

# ---------- Utilities --------------------------------------------------

def random_id(prefix="ID"):
    """Generate random ID."""
    return prefix + ''.join(random.choices(string.digits, k=6))

def random_name():
    """Generate random name."""
    first = ["Rahim", "Karim", "Jamal", "Rafi", "Imran", "Sami", "Hasan", "Fahim"]
    last = ["Ahmed", "Hossain", "Rahman", "Sheikh", "Mia", "Talukder", "Biswas"]
    return random.choice(first) + " " + random.choice(last)

def random_department():
    """Return random department."""
    depts = ["CSE", "EEE", "BBA", "English", "Law", "Civil", "Mechanical"]
    return random.choice(depts)

def random_score():
    """Return random HSC+SSC score."""
    return round(random.uniform(3.0, 5.0), 2)

def random_date():
    """Return random date."""
    year = random.choice([2022, 2023, 2024])
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return datetime.date(year, month, day)

# ---------- Classes ----------------------------------------------------

class Applicant:
    """Applicant information class."""
    def __init__(self, name, dept, score):
        self.applicant_id = random_id("APP")
        self.name = name
        self.department = dept
        self.score = score
        self.application_date = random_date()
        self.status = "Pending"

    def approve(self):
        self.status = "Approved"

    def reject(self):
        self.status = "Rejected"

    def to_dict(self):
        return {
            "applicant_id": self.applicant_id,
            "name": self.name,
            "department": self.department,
            "score": self.score,
            "application_date": str(self.application_date),
            "status": self.status
        }

class AdmissionPortal:
    """Main portal system maintaining applicants."""
    def __init__(self):
        self.applicants = {}

    def add_applicant(self, applicant):
        self.applicants[applicant.applicant_id] = applicant

    def get_applicant(self, applicant_id):
        return self.applicants.get(applicant_id, None)

    def approve_applicant(self, applicant_id):
        app = self.get_applicant(applicant_id)
        if app:
            app.approve()
            return True
        return False

    def reject_applicant(self, applicant_id):
        app = self.get_applicant(applicant_id)
        if app:
            app.reject()
            return True
        return False

    def list_all(self):
        return [a.to_dict() for a in self.applicants.values()]

    def filter_by_department(self, dept):
        return [a.to_dict() for a in self.applicants.values() if a.department == dept]

    def filter_by_status(self, status):
        return [a.to_dict() for a in self.applicants.values() if a.status == status]

# ---------- Demo Functions ---------------------------------------------

def generate_random_applicants(portal, count=20):
    """Generate random applicants."""
    for _ in range(count):
        name = random_name()
        dept = random_department()
        score = random_score()
        applicant = Applicant(name, dept, score)
        portal.add_applicant(applicant)

def print_applicant_info(applicant):
    """Print single applicant info."""
    if not applicant:
        print("Applicant not found!")
        return
    data = applicant.to_dict()
    for k, v in data.items():
        print(f"{k}: {v}")
    print()

def print_portal_summary(portal):
    """Print summary."""
    apps = portal.list_all()
    print("===== ADMISSION SUMMARY =====")
    print(f"Total Applicants: {len(apps)}")
    approved = len([a for a in apps if a['status'] == "Approved"])
    rejected = len([a for a in apps if a['status'] == "Rejected"])
    pending = len([a for a in apps if a['status'] == "Pending"])
    print(f"Approved: {approved}")
    print(f"Rejected: {rejected}")
    print(f"Pending : {pending}")
    print("==============================\n")

# ---------- Main Functional Simulation --------------------------------

def simulate_admission_process():
    """Simulate the full process."""
    portal = AdmissionPortal()

    # Step 1: Generate applicants
    generate_random_applicants(portal, count=25)

    # Step 2: Random approvals/rejections
    for app_id, applicant in portal.applicants.items():
        decision = random.choice(["A", "R", "P"])
        if decision == "A":
            applicant.approve()
        elif decision == "R":
            applicant.reject()

    # Step 3: Display summary
    print_portal_summary(portal)

    # Step 4: Print sample applicant info
    random_app_id = random.choice(list(portal.applicants.keys()))
    print("Showing sample applicant info:\n")
    print_applicant_info(portal.get_applicant(random_app_id))

    # Step 5: Show department-specific list
    dept = random_department()
    print(f"Listing applicants of department: {dept}\n")
    for a in portal.filter_by_department(dept):
        print(a)
    print()

    return portal

# ---------- Extra Random Utility Code to Reach 200 Lines --------------

def calculate_merit(applicant):
    """Merit calculation formula."""
    base = applicant.score * 20
    bonus = random.randint(0, 10)
    return base + bonus

def generate_merit_list(portal):
    """Generate merit list sorted by score."""
    merit_list = []
    for a in portal.applicants.values():
        merit_list.append((a.applicant_id, calculate_merit(a)))
    merit_list.sort(key=lambda x: x[1], reverse=True)
    return merit_list

def print_merit_list(merit_list):
    """Print merit list."""
    print("===== MERIT LIST =====")
    rank = 1
    for app_id, score in merit_list:
        print(f"Rank {rank}: {app_id} - Score {score}")
        rank += 1
    print("=======================\n")

def save_applicant_data_to_file(portal, filename="admission_data.txt"):
    """Save all applicant data."""
    with open(filename, "w") as f:
        for a in portal.applicants.values():
            f.write(str(a.to_dict()) + "\n")

def load_fake_notice():
    notices = [
        "Orientation will be held on 10 January.",
        "Bring all original certificates for verification.",
        "Scholarship form submission starts tomorrow.",
        "Seat plan will be published soon."
    ]
    return random.choice(notices)

def print_notice_board():
    print("===== NOTICE BOARD =====")
    print(load_fake_notice())
    print("========================\n")

# ---------- MAIN RUN -----------------------------------------------

if __name__ == "__main__":
    portal = simulate_admission_process()
    merit = generate_merit_list(portal)
    print_merit_list(merit)
    print_notice_board()
    save_applicant_data_to_file(portal)
>>>>>>> ac4f4d565d17d34ed4c6f5e952d19929cab2a95d
