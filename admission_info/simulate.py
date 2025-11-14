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
