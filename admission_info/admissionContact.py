import re
import datetime

CONTACT_DB = []
CONTACT_ID_COUNTER = 1

class AdmissionContact:
    def __init__(self, name, email, phone, message):
        global CONTACT_ID_COUNTER
        self.id = CONTACT_ID_COUNTER
        CONTACT_ID_COUNTER += 1
        self.name = name
        self.email = email
        self.phone = phone
        self.message = message
        self.timestamp = datetime.datetime.now()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "message": self.message,
            "timestamp": str(self.timestamp)
        }

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def is_valid_phone(phone):
    return phone.isdigit() and (8 <= len(phone) <= 15)

def is_valid_name(name):
    return bool(re.match(r"^[A-Za-z ]+$", name))

def is_valid_message(msg):
    return len(msg.strip()) >= 5

def create_contact(name, email, phone, message):
    if not is_valid_name(name):
        return {"error": "Invalid name"}
    if not is_valid_email(email):
        return {"error": "Invalid email"}
    if not is_valid_phone(phone):
        return {"error": "Invalid phone number"}
    if not is_valid_message(message):
        return {"error": "Message too short"}
    contact = AdmissionContact(name, email, phone, message)
    CONTACT_DB.append(contact)
    log_event(f"New contact received (ID={contact.id})")
    return {"success": True, "contact": contact.to_dict()}

def get_contact(contact_id):
    for c in CONTACT_DB:
        if c.id == contact_id:
            return c.to_dict()
    return {"error": "Contact not found"}

def get_all_contacts():
    return [c.to_dict() for c in CONTACT_DB]

def search_by_name(keyword):
    keyword = keyword.lower()
    return [c.to_dict() for c in CONTACT_DB if keyword in c.name.lower()]

def search_by_email(email):
    return [c.to_dict() for c in CONTACT_DB if c.email == email]

def filter_by_date(start, end):
    results = []
    for c in CONTACT_DB:
        if start <= c.timestamp.date() <= end:
            results.append(c.to_dict())
    return results

LOGS = []

def log_event(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    LOGS.append(f"[{timestamp}] {msg}")

def get_logs():
    return LOGS

def delete_contact(cid):
    global CONTACT_DB
    new_db = [c for c in CONTACT_DB if c.id != cid]
    if len(new_db) == len(CONTACT_DB):
        return {"error": "ID not found"}
    CONTACT_DB = new_db
    log_event(f"Contact ID {cid} deleted")
    return {"success": True}

def update_contact(cid, name=None, email=None, phone=None, message=None):
    for c in CONTACT_DB:
        if c.id == cid:
            if name and is_valid_name(name):
                c.name = name
            if email and is_valid_email(email):
                c.email = email
            if phone and is_valid_phone(phone):
                c.phone = phone
            if message and is_valid_message(message):
                c.message = message
            log_event(f"Contact ID {cid} updated")
            return {"success": True, "contact": c.to_dict()}
    return {"error": "Contact not found"}

def seed_dummy_contacts():
    create_contact("Mahmud Alam", "mahmud@gmail.com", "01710000000", "Admission query")
    create_contact("Aisha Noor", "aisha@yahoo.com", "01300000000", "Scholarship info?")
    create_contact("Rafi Ahmed", "rafi@example.com", "01500000000", "Admission requirements?")
    return True

def export_contacts_json():
    data = get_all_contacts()
    return {"count": len(data), "contacts": data}

def count_contacts():
    return len(CONTACT_DB)

def contact_exists(email):
    for c in CONTACT_DB:
        if c.email == email:
            return True
    return False

def get_recent_contacts(n):
    return [c.to_dict() for c in CONTACT_DB[-n:]]

def clear_contacts():
    global CONTACT_DB
    CONTACT_DB = []
    return True

def get_contact_ids():
    return [c.id for c in CONTACT_DB]

def get_messages():
    return [c.message for c in CONTACT_DB]

def longest_message():
    if not CONTACT_DB:
        return None
    return max(CONTACT_DB, key=lambda x: len(x.message)).to_dict()

def shortest_message():
    if not CONTACT_DB:
        return None
    return min(CONTACT_DB, key=lambda x: len(x.message)).to_dict()

def first_contact():
    if CONTACT_DB:
        return CONTACT_DB[0].to_dict()
    return None

def last_contact():
    if CONTACT_DB:
        return CONTACT_DB[-1].to_dict()
    return None

def list_names():
    return [c.name for c in CONTACT_DB]

def list_emails():
    return [c.email for c in CONTACT_DB]

def list_phones():
    return [c.phone for c in CONTACT_DB]

def search_message(keyword):
    keyword = keyword.lower()
    return [c.to_dict() for c in CONTACT_DB if keyword in c.message.lower()]

def contacts_on_date(date):
    return [c.to_dict() for c in CONTACT_DB if c.timestamp.date() == date]

def total_logs():
    return len(LOGS)

def clear_logs():
    LOGS.clear()
    return True

def fake_bulk_generate(n):
    for i in range(n):
        create_contact(f"User{i}", f"user{i}@mail.com", "01711111111", "Hello")
    return True

def get_contact_by_index(i):
    if i < 0 or i >= len(CONTACT_DB):
        return None
    return CONTACT_DB[i].to_dict()

def reverse_contacts():
    return [c.to_dict() for c in reversed(CONTACT_DB)]

def sorted_by_name():
    return [c.to_dict() for c in sorted(CONTACT_DB, key=lambda x: x.name)]

def sorted_by_date():
    return [c.to_dict() for c in sorted(CONTACT_DB, key=lambda x: x.timestamp)]

def messages_length_list():
    return [len(c.message) for c in CONTACT_DB]

def emails_starting_with(letter):
    return [c.to_dict() for c in CONTACT_DB if c.email.startswith(letter)]

def phones_by_prefix(prefix):
    return [c.to_dict() for c in CONTACT_DB if c.phone.startswith(prefix)]

def all_data():
    return {"contacts": get_all_contacts(), "logs": LOGS}

if __name__ == "__main__":
    seed_dummy_contacts()
    print(get_all_contacts())
    print(get_logs())
    delete_contact(1)
    print(get_logs())
    update_contact(2, name="Updated User")
    print(export_contacts_json())
    print(sorted_by_name())
    print(sorted_by_date())
    print(longest_message())
    print(shortest_message())
    print(count_contacts())
    fake_bulk_generate(5)
    print(count_contacts())
    print(reverse_contacts())
    clear_logs()
    print(total_logs())
    print(list_names())
    print(get_recent_contacts(2))
    print(search_message("info"))
    print(contact_exists("aisha@yahoo.com"))
    print(get_messages())
    print(all_data())
    print(first_contact())
    print(last_contact())
    print(list_emails())
    print(phones_by_prefix("017"))
    clear_contacts()
    print(get_all_contacts())
    print("Done")