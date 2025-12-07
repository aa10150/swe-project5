import os
import sys
import time

from dotenv import load_dotenv

from .app_db import connect_db, seed_db

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/course_planner")
DB_NAME = os.getenv("MONGO_DB_NAME", "course_planner")
WAIT = int(os.getenv("WAIT_BEFORE_CONNECT", "2"))
ENV = os.getenv("ENVIRONMENT", "development")

if WAIT:
    time.sleep(WAIT)

try:
    db = connect_db(MONGO_URI, DB_NAME)
except Exception as e:
    print("Failed to connect to MongoDB:", e)
    sys.exit(1)

result = seed_db(db, environment=ENV)
print("Seed complete:", result)
