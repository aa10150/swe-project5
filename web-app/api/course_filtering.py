"""
course_filtering.py

Module for filtering and validating courses based on prerequisites,
semester availability, and student completion status.
"""

import os
from typing import Dict, List, Optional

from pymongo import MongoClient

from api.major_requirements import get_math_course_info, is_math_course

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
        course for course in courses if course.get("course_code") not in completed_set
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


def check_prerequisites_met(
    course: Dict, completed_courses: List[str], all_courses: List[Dict]
) -> bool:
    """
    Verify that prerequisites for a course are satisfied.

    Supports both AND and OR logic:
    - Simple list: ["A", "B"] = OR logic (any one required) - backward compatible
    - Object with logic: {"logic": "and", "courses": ["A", "B"]} = AND logic (all required)
    - Object with logic: {"logic": "or", "courses": ["A", "B"]} = OR logic (any one required)

    Args:
        course: Course dictionary with 'prerequisites' field
        completed_courses: List of course codes the student has completed
        all_courses: List of all course dictionaries from database

    Returns:
        True if prerequisites are met, False otherwise
    """
    prerequisites = course.get("prerequisites", [])

    # No prerequisites means requirement is met
    if not prerequisites:
        return True

    completed_set = set(completed_courses)

    # Handle different prerequisite structures
    return _evaluate_prerequisites(prerequisites, completed_set, all_courses)


def _evaluate_prerequisites(
    prerequisites, completed_set: set, all_courses: List[Dict]
) -> bool:
    """
    Evaluate prerequisites based on their structure.

    Args:
        prerequisites: Can be:
            - List of strings: ["A", "B"] = OR logic (backward compatible)
            - Dict with "logic" and "courses": {"logic": "and", "courses": ["A", "B"]}
              or {"logic": "or", "courses": ["A", "B"]}
        completed_set: Set of completed course codes
        all_courses: List of all course dictionaries (for future use if needed)

    Returns:
        True if prerequisites are met
    """
    # Simple list = OR logic (backward compatible)
    if isinstance(prerequisites, list):
        # Check if any prerequisite is completed
        return any(prereq_code in completed_set for prereq_code in prerequisites)

    # Dictionary structure with explicit logic
    if isinstance(prerequisites, dict):
        if "logic" in prerequisites and "courses" in prerequisites:
            logic = prerequisites["logic"].lower()
            courses = prerequisites["courses"]

            if logic == "and":
                # All courses must be completed
                return all(course_code in completed_set for course_code in courses)
            elif logic == "or":
                # Any course must be completed
                return any(course_code in completed_set for course_code in courses)
            else:
                # Unknown logic, default to OR
                return any(course_code in completed_set for course_code in courses)

    # Unknown structure, default to False
    return False


def filter_by_prerequisites(
    courses: List[Dict], completed_courses: List[str], all_courses: List[Dict]
) -> List[Dict]:
    """
    Return only courses where all prerequisites are satisfied.

    Args:
        courses: List of course dictionaries to filter
        completed_courses: List of course codes the student has completed
        all_courses: List of all course dictionaries from database

    Returns:
        List of courses where prerequisites are met
    """
    return [
        course
        for course in courses
        if check_prerequisites_met(course, completed_courses, all_courses)
    ]
