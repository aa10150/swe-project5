import os
from pymongo import MongoClient

# Mongo connection (use your own URI, or default local)
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://database:27017/nyu_cs_planner")
DB_NAME = "nyu_cs_planner"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Clear existing
db.courses.delete_many({})
db.students.delete_many({})

# Seed courses — sample from NYU CS catalog
courses = [
    {
        "course_code": "CSCI-UA.0002",
        "name": "Introduction to Computer Programming (No Prior Experience)",
        "subject": "CSCI-UA",
        "category": "CS Foundation",
        "credits": 4,
        "difficulty": 2,
        "prerequisites": [],
    },
    {
        "course_code": "CSCI-UA.0101",
        "name": "Introduction to Computer Science",
        "subject": "CSCI-UA",
        "category": "CS Requirement",
        "credits": 4,
        "difficulty": 2,
        "prerequisites": ["CSCI-UA.0002"],
    },
    {
        "course_code": "CSCI-UA.0102",
        "name": "Data Structures",
        "subject": "CSCI-UA",
        "category": "CS Requirement",
        "credits": 4,
        "difficulty": 3,
        "prerequisites": ["CSCI-UA.0101"],
    },
    {
        "course_code": "CSCI-UA.0201",
        "name": "Computer Systems Organization",
        "subject": "CSCI-UA",
        "category": "CS Requirement",
        "credits": 4,
        "difficulty": 3,
        "prerequisites": ["CSCI-UA.0102"],
    },
    {
        "course_code": "CSCI-UA.0202",
        "name": "Operating Systems",
        "subject": "CSCI-UA",
        "category": "CS Requirement",
        "credits": 4,
        "difficulty": 5,
        "prerequisites": ["CSCI-UA.0201"],
    },
    {
        "course_code": "CSCI-UA.0310",
        "name": "Basic Algorithms",
        "subject": "CSCI-UA",
        "category": "CS Requirement",
        "credits": 4,
        "difficulty": 4,
        "prerequisites": ["CSCI-UA.0102"],
    },
    {
        "course_code": "CSCI-UA.0472",
        "name": "Artificial Intelligence",
        "subject": "CSCI-UA",
        "category": "CS Elective",
        "credits": 4,
        "difficulty": 4,
        "prerequisites": ["CSCI-UA.0201", "CSCI-UA.0310"],
    },
    {
        "course_code": "CSCI-UA.0474",
        "name": "Software Engineering",
        "subject": "CSCI-UA",
        "category": "CS Elective",
        "credits": 4,
        "difficulty": 3,
        "prerequisites": ["CSCI-UA.0201"],
    },
]

# Insert courses
db.courses.insert_many(courses)
print(f"Inserted {len(courses)} courses into db.")

# Seed a couple sample students
students = [
    {
        "netId": "student1",
        "name": "Alice Example",
        "year": "Freshman",
        "major": "Computer Science",
        "interests": ["AI", "Systems"],
        "completedCourses": [],
        "plannedSemesters": [],
    },
    {
        "netId": "student2",
        "name": "Bob Example",
        "year": "Sophomore",
        "major": "Computer Science",
        "interests": ["Software Engineering"],
        "completedCourses": ["CSCI-UA.0101"],
        "plannedSemesters": [],
    },
]

db.students.insert_many(students)
print(f"Inserted {len(students)} students into db.")
