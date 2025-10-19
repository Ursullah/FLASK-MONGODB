from flask_pymongo import PyMongo

mongo = None

def init_db(app):
    """Initialize MongoDB connection"""
    global mongo
    mongo = PyMongo(app)
    return mongo


# ---------- USER OPERATIONS ----------
def find_user_by_email(email):
    return mongo.db.users.find_one({"email": email})


def add_user(email, password):
    mongo.db.users.insert_one({"email": email, "password": password})


def update_user_password(email, new_password):
    mongo.db.users.update_one({"email": email}, {"$set": {"password": new_password}})


# ---------- CONTACT OPERATIONS ----------
def add_contact(contact_data):
    mongo.db.contacts.insert_one(contact_data)


def find_contact_by_reg_number(reg_number):
    return mongo.db.contacts.find_one({"reg_number": reg_number})
