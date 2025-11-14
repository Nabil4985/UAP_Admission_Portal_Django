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

