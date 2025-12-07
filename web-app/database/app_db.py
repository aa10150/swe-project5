"""
database/app_db.py

Small module exposing DB helper functions so tests can import them.
Provides:
- connect_db(uri, dbname)
- seed_db(db)            # insert courses + students
- create_indexes(db)
"""

import os


import bcrypt
from dotenv import load_dotenv
from pymongo import MongoClient

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME")

if not MONGO_URI or not DB_NAME:
    raise ValueError(
        "MONGO_URI or MONGO_DB_NAME not set in environment variables or .env file."
    )


COURSES = [
    {
        "course_code": "CORE-UA.0109",
        "title": "Quantitative Reasoning: Mathematics & Computing",
        "type": "Other",
        "subject": "CORE-UA",
        "difficulty": 2,
        "credits": 4,
        "prerequisites": [],
        "description": "This course teaches key mathematical concepts using the Python programming language, focusing on basic features of Python, phenomena of growth and decay (exponentials, logarithms), trigonometry, counting problems, and probability. No prior programming knowledge is required.",
        "semester_offered": ["Fall"],
    },
    {
        "course_code": "CSCI-UA.0002",
        "title": "Introduction to Computer Programming (No Prior Experience)",
        "type": "CS Foundation",
        "subject": "CSCI-UA",
        "difficulty": 2,
        "credits": 4,
        "prerequisites": [],
        "description": "An introduction to the fundamentals of computer programming. Students design, write, and debug computer programs. Does not count toward the computer science major.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "CSCI-UA.0003",
        "title": "Introduction to Computer Programming (Limited Prior Experience)",
        "type": "CS Foundation",
        "subject": "CSCI-UA",
        "difficulty": 2,
        "credits": 4,
        "prerequisites": [],
        "description": "Introduces object-oriented programming, recursion, and other important concepts to students who already have had some exposure to programming in the context of building applications using Python. Does not count toward the computer science major.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0004",
        "title": "Introduction to Web Design & Computer Principles",
        "type": "Other/Non-Major",
        "subject": "CSCI-UA",
        "difficulty": 1,
        "credits": 4,
        "prerequisites": [],
        "description": "Introduces the practice of web design and basic principles of computer science, covering web design, graphics and software tools, an overview of hardware/software, and the history and impact of computers and the Internet.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "CSCI-UA.0060",
        "title": "Database Design and Implementation",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 3,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0002", "CSCI-UA.0003"],
        "description": "Introduces principles and applications of database design and working with data. Students use Python and SQL to study relational and NoSQL databases.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0061",
        "title": "Web Development and Programming",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 3,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0002", "CSCI-UA.0003", "CSCI-UA.0004"],
        "description": "Provides a practical approach to web technologies and programming, focusing on building interactive, secure, and powerful web programs using client and server side technologies.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0101",
        "title": "Introduction to Computer Science",
        "type": "CS Requirement",
        "subject": "CSCI-UA",
        "difficulty": 3,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0002", "CSCI-UA.0003"],
        "description": "How to design algorithms to solve problems and how to translate these algorithms into working computer programs. Intended primarily for computer science majors.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "CSCI-UA.0102",
        "title": "Data Structures",
        "type": "CS Requirement",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0101"],
        "description": "Focuses on the use and design of data structures (stacks, queues, linked lists, binary trees), their implementation in a high-level language, and analysis of their effect on algorithm efficiency.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "CSCI-UA.0201",
        "title": "Computer Systems Organization",
        "type": "CS Requirement",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0102"],
        "description": "Covers the internal structure of computers, machine (assembly) language programming, the use of pointers, logical design of computers, computer architecture, and internal representation of data.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "CSCI-UA.0202",
        "title": "Operating Systems",
        "type": "CS Requirement",
        "subject": "CSCI-UA",
        "difficulty": 5,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201"],
        "description": "Covers the principles and design of operating systems, including process scheduling and synchronization, deadlocks, memory management (virtual memory), input/output, and file systems.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0310",
        "title": "Basic Algorithms",
        "type": "CS Requirement",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0102"],
        "description": "Introduction to the study of algorithms, presenting two main themes: designing appropriate data structures and analyzing the efficiency of algorithms that use them. Algorithms studied include sorting, searching, and graph algorithms. [Also requires Discrete Mathematics and a Calculus course.]",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "CSCI-UA.0330",
        "title": "Introduction to Computer Simulation",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 3,
        "credits": 4,
        "prerequisites": [],
        "description": "Students learn how to do computer simulations of phenomena such as orbits, disease epidemics, musical instruments, and traffic flow, based on mathematical models, numerical methods, and Matlab programming techniques. [Requires Calculus I/Math for Economics II and General Physics.]",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "CSCI-UA.0421",
        "title": "Numerical Computing",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201"],
        "description": "Covers floating-point arithmetic, the IEEE standard, and fundamental numerical algorithms (direct, iterative, and discretization methods). Uses graphics and software packages such as Matlab. [Also requires Calculus I/Math for Economics and Linear Algebra.]",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "CSCI-UA.0430",
        "title": "Agile Software Development and DevOps",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 3,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201"],
        "description": "Students will understand the core methodologies, technologies, and tools used in Agile software development and DevOps to manage changing requirements, automate tasks, and increase the speed, robustness, and scalability of software development.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0453",
        "title": "Theory of Computation",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 5,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0310", "CSCI-UA.0201"],
        "description": "A mathematical approach to studying topics in computer science, such as regular languages (finite automata, regular expressions), context-free languages, and an introduction to computability theory and NP-completeness.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "CSCI-UA.0467",
        "title": "Applied Internet Technology",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201"],
        "description": "A practical introduction to creating modern web applications, covering full-stack development including server programming, database implementation, and frontend technologies.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0474",
        "title": "Software Engineering",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 3,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201"],
        "description": "Covers methods of software engineering, including advanced object-oriented design, design patterns, refactoring, universal modeling language, and development tools. Culminates in a semester-long group project.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0475",
        "title": "Predictive Analytics",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201", "CSCI-UA.0310"],
        "description": "Introduces the art and science of extracting information from data to predict future trends. Covers the analytics life-cycle, data preprocessing, clustering, classification, and other machine learning algorithms. [Also requires Linear Algebra.]",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0476",
        "title": "PROCESSING BIG DATA FOR ANALYTICS APPLICATIONS",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201", "CSCI-UA.0310"],
        "description": "Introduces platforms, tools, and architectures for scalable management and processing of big data. Provides hands-on experience with distributed processing Apache solutions such as Hadoop, Spark, Hive, and Kafka.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0478",
        "title": "Introduction to Cryptography",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0310"],
        "description": "An introduction to the principles and practice of cryptography and its application to network security, including symmetric-key encryption and block ciphers.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0479",
        "title": "Data Management and Analysis",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 3,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0102"],
        "description": "Introduces principles and applications of data management and analysis. Note: Students who successfully complete this course are NOT eligible to take Database Design and Implementation (CSCI-UA.0060).",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0520",
        "title": "Undergraduate Research",
        "type": "Other/Special",
        "subject": "CSCI-UA",
        "difficulty": 0,
        "credits": "1 - 4",
        "prerequisites": [],
        "description": "The student is supervised by a faculty member actively engaged in research, potentially leading to publishable results. May be one or two semesters. Honors students write an honors thesis. [Requires permission of the department.]",
        "semester_offered": ["Fall"],
    },
    {
        "course_code": "CSCI-UA.0521",
        "title": "Undergraduate Research",
        "type": "Other/Special",
        "subject": "CSCI-UA",
        "difficulty": 0,
        "credits": "1 - 4",
        "prerequisites": [],
        "description": "Continuation of supervised research with a faculty member. A substantial commitment to this work is expected. [Requires permission of the department.]",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "CSCI-UA.0897",
        "title": "Internship",
        "type": "Other/Special",
        "subject": "CSCI-UA",
        "difficulty": 0,
        "credits": "1 - 4",
        "prerequisites": [],
        "description": "An excellent complement to formal course work, providing practical training and hands-on experience. Credit does not count toward the major. [Restricted to declared majors with specific GPA requirements.]",
        "semester_offered": ["Fall"],
    },
    {
        "course_code": "CSCI-UA.0898",
        "title": "Internship",
        "type": "Other/Special",
        "subject": "CSCI-UA",
        "difficulty": 0,
        "credits": "1 - 4",
        "prerequisites": [],
        "description": "An excellent complement to formal course work, providing practical training and hands-on experience. Credit does not count toward the major. [Restricted to declared majors with specific GPA requirements.]",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "CSCI-UA.0997",
        "title": "Independent Study",
        "type": "Other/Special",
        "subject": "CSCI-UA",
        "difficulty": 0,
        "credits": "1 - 4",
        "prerequisites": [],
        "description": "Students work on an individual basis under the supervision of a full-time faculty member. Does not satisfy the major elective requirement. [Requires permission of the department and specific GPA requirements.]",
        "semester_offered": ["Fall"],
    },
    {
        "course_code": "CSCI-UA.0998",
        "title": "Independent Study",
        "type": "Other/Special",
        "subject": "CSCI-UA",
        "difficulty": 0,
        "credits": "1 - 4",
        "prerequisites": [],
        "description": "Students work on an individual basis under the supervision of a full-time faculty member. Does not satisfy the major elective requirement. [Requires permission of the department and specific GPA requirements.]",
        "semester_offered": ["Spring"],
    },
]


STUDENTS = [
    {
        "name": "Freshman Overzealous",
        "netid": "fresh01",
        "email": "fresh01@example.edu",
        "password": "test123",
        "year": "Freshman",
        "major": "Computer Science",
        "interests": ["AI", "Systems"],
        "completed_courses": [],
        "planned_semesters": [],
    },
    {
        "name": "Sophomore Balanced",
        "netid": "soph01",
        "email": "soph01@example.edu",
        "password": "test123",
        "year": "Sophomore",
        "major": "Computer Science",
        "interests": ["Software Engineering"],
        "completed_courses": ["CSCI-UA.0101", "CSCI-UA.0102"],
        "planned_semesters": [],
    },
]

# Hash passwords for students before inserting into DB
for student in STUDENTS:
    plain_pw = student["password"].encode()
    hashed_pw = bcrypt.hashpw(plain_pw, bcrypt.gensalt())
    student["password"] = hashed_pw.decode()  # store as string


def connect_db(uri=None, db_name=None):
    """Return db handle."""
    uri = uri or MONGO_URI
    db_name = db_name or DB_NAME
    return MongoClient(uri)[db_name]


def create_indexes(db):
    """Create useful indexes (idempotent)."""
    db.courses.create_index("course_code", unique=True)
    db.students.create_index("netid", unique=True)


def seed_db(db, environment="development"):
    """
    Seed the DB with sample courses and students.
    In production, do NOT clear collections to avoid deleting users.
    """
    clear_first = environment != "production"

    if clear_first:
        db.courses.drop()
        db.students.drop()

    db.courses.insert_many(COURSES)
    if clear_first:
        db.students.insert_many(STUDENTS)

    create_indexes(db)

    return {
        "courses": len(COURSES),
        "students": len(STUDENTS) if clear_first else "existing preserved",
    }
