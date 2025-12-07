import os

import bcrypt
from mongomock import DuplicateKeyError
from pymongo import MongoClient


MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def create_user(email, password, name):
    """Create a new user with full structure.
    Returns the inserted user or None if already exists."""

    # Hash password
    hashed_pw = bcrypt.hashpw(
        password.encode(), bcrypt.gensalt()
    ).decode()  # store as string

    new_user = {
        "name": name,
        "netid": email.split("@")[0],
        "email": email,
        "password": hashed_pw,  # store hashed password
        "year": "",
        "major": "",
        "interests": [],
        "completed_courses": [],
        "planned_semesters": [],
    }

    try:
        db.students.insert_one(new_user)
        return new_user
    except DuplicateKeyError:
        return None


def verify_user(email, password):
    user = db.students.find_one({"email": email})
    if not user:
        return None

    # Check hashed password
    if not bcrypt.checkpw(password.encode(), user["password"].encode()):
        return None

    return user
