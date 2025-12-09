"""
course_filtering.py

Module for filtering and validating courses based on prerequisites,
semester availability, and student completion status.
"""

import os
from typing import Dict, List, Optional

from pymongo import MongoClient

from api.major_requirements import get_math_course_info

# Database connection (following pattern from user_model.py)
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def get_all_courses_from_db() -> List[Dict]:
    """
    Fetch all courses from MongoDB courses collection.

    Returns:
        List of course dictionaries with all course metadata
    """
    courses_cursor = db.courses.find({})
    courses = list(courses_cursor)
    return courses


def filter_completed_courses(
    courses: List[Dict], completed_codes: List[str]
) -> List[Dict]:
    """
    Remove courses that the student has already completed.

    Args:
        courses: List of course dictionaries
        completed_codes: List of course codes the student has completed

    Returns:
        List of courses not in completed_codes
    """
    completed_set = set(completed_codes)
    return [
        course
        for course in courses
        if course.get("course_code") not in completed_set
    ]


def get_course_by_code(course_code: str, all_courses: List[Dict]) -> Optional[Dict]:
    """
    Find a course by its course code. Checks both database courses and math courses.

    Args:
        course_code: Course code to search for (e.g., "CSCI-UA.0101" or "MATH-UA.0121")
        all_courses: List of all course dictionaries from database

    Returns:
        Course dictionary with normalized structure, or None if not found.
        Normalized structure uses 'title' for name (DB courses have 'title', math courses have 'name')
    """
    # First check in database courses
    for course in all_courses:
        if course.get("course_code") == course_code:
            return course

    # If not found, check math courses
    math_course = get_math_course_info(course_code)
    if math_course:
        # Normalize math course structure to match DB courses
        # Math courses have 'name', DB courses have 'title'
        normalized_course = math_course.copy()
        normalized_course["title"] = normalized_course.pop("name", "")
        # Add default fields that math courses might not have
        normalized_course.setdefault("prerequisites", [])
        normalized_course.setdefault("semester_offered", [])
        normalized_course.setdefault("credits", 4)
        normalized_course.setdefault("difficulty", 0)
        normalized_course.setdefault("description", "")
        return normalized_course

    return None

