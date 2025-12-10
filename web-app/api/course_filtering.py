"""
course_filtering.py

Module for filtering and validating courses based on prerequisites,
semester availability, and student completion status.
"""

import os
from typing import Dict, List, Optional

from pymongo import MongoClient

from api.major_requirements import (
    get_math_course_info,
    get_major_requirements,
    is_math_course,
    MATH_COURSES,
)

# Database connection (following pattern from user_model.py)
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME")

if not MONGO_URI or not DB_NAME:
    print(
        f"WARNING: MONGO_URI or DB_NAME not set. MONGO_URI={MONGO_URI}, DB_NAME={DB_NAME}"
    )
    client = None
    db = None
else:
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
    except Exception as e:
        print(f"ERROR: Failed to connect to MongoDB: {e}")
        client = None
        db = None


def get_all_courses_from_db() -> List[Dict]:
    """
    Fetch all courses from MongoDB courses collection.

    Returns:
        List of course dictionaries with all course metadata
    """
    if db is None:
        print("ERROR: Database connection not available")
        return []

    try:
        courses_cursor = db.courses.find({})
        courses = list(courses_cursor)
        print(f"DEBUG: Retrieved {len(courses)} courses from database")
        return courses
    except Exception as e:
        print(f"ERROR: Failed to fetch courses from database: {e}")
        return []


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
    - Simple list: ["A", "B"] = AND logic (all required)
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
            - List of strings: ["A", "B"] = AND logic (all required)
            - Dict with "logic" and "courses": {"logic": "and", "courses": ["A", "B"]}
              or {"logic": "or", "courses": ["A", "B"]}
        completed_set: Set of completed course codes
        all_courses: List of all course dictionaries (for future use if needed)

    Returns:
        True if prerequisites are met
    """
    # Simple list = AND logic (all prerequisites must be completed)
    if isinstance(prerequisites, list):
        # Check if ALL prerequisites are completed
        return all(prereq_code in completed_set for prereq_code in prerequisites)

    # Dictionary structure with explicit logic
    if isinstance(prerequisites, dict):
        if "logic" in prerequisites and "courses" in prerequisites:
            logic = prerequisites["logic"].lower()
            courses = prerequisites["courses"]

            if logic == "and":
                # All courses must be completed
                return all(course_code in completed_set for course_code in courses)
            if logic == "or":
                # Any course must be completed
                return any(course_code in completed_set for course_code in courses)
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


def _extract_semester_type(semester_name: str) -> Optional[str]:
    """
    Extract semester type (Fall, Spring, Summer) from semester name.

    Args:
        semester_name: Semester name like "Freshman Fall", "Sophomore Spring", etc.

    Returns:
        "Fall", "Spring", "Summer", or None if not found
    """
    semester_name_lower = semester_name.lower()

    if "fall" in semester_name_lower:
        return "Fall"
    if "spring" in semester_name_lower:
        return "Spring"
    if "summer" in semester_name_lower:
        return "Summer"

    return None


def filter_by_semester_availability(
    courses: List[Dict], target_semester: str
) -> List[Dict]:
    """
    Filter courses to only those offered in the target semester.

    Args:
        courses: List of course dictionaries to filter
        target_semester: Semester name like "Freshman Fall", "Sophomore Spring", etc.

    Returns:
        List of courses offered in the target semester
    """
    semester_type = _extract_semester_type(target_semester)

    if not semester_type:
        # If we can't extract semester type, return all courses
        return courses

    filtered_courses = []
    for course in courses:
        semesters_offered = course.get("semester_offered", [])
        if semester_type in semesters_offered:
            filtered_courses.append(course)

    return filtered_courses


def _get_math_courses_for_semester(
    target_semester: str, major_name: Optional[str] = None
) -> List[Dict]:
    """
    Get math courses that are available in the target semester.

    Checks major requirements for math courses with semester information,
    or falls back to all math courses if no major is specified.

    Args:
        target_semester: Semester name like "Freshman Fall"
        major_name: Optional major name to get major-specific math courses

    Returns:
        List of math course dictionaries normalized to match DB course structure
    """
    semester_type = _extract_semester_type(target_semester)
    if not semester_type:
        return []

    math_courses = []

    # If major is specified, check major requirements for math courses
    if major_name:
        major_reqs = get_major_requirements(major_name)
        if major_reqs:
            # Check core requirements for math courses
            core_reqs = major_reqs.get("core_requirements", {}).get("courses", [])
            for req in core_reqs:
                if req.get("is_math_course") and req.get("course_code"):
                    semesters_offered = req.get("semesters_offered", [])
                    if semester_type in semesters_offered:
                        math_course = get_math_course_info(req["course_code"])
                        if math_course:
                            normalized = math_course.copy()
                            normalized["title"] = normalized.pop("name", "")
                            normalized["semester_offered"] = semesters_offered
                            normalized.setdefault(
                                "prerequisites", req.get("prerequisites", [])
                            )
                            normalized.setdefault("credits", 4)
                            normalized.setdefault("difficulty", 0)
                            normalized.setdefault("description", "")
                            math_courses.append(normalized)

            # Check elective substitutions for math courses
            elective_reqs = major_reqs.get("elective_requirements", {})
            substitutions = elective_reqs.get("substitutions", {})
            if substitutions.get("allowed", False):
                substitution_courses = substitutions.get("courses", [])
                for sub_course in substitution_courses:
                    if sub_course.get("is_math_course") and sub_course.get(
                        "course_code"
                    ):
                        semesters_offered = sub_course.get("semesters_offered", [])
                        if semester_type in semesters_offered:
                            math_course = get_math_course_info(
                                sub_course["course_code"]
                            )
                            if math_course:
                                normalized = math_course.copy()
                                normalized["title"] = normalized.pop("name", "")
                                normalized["semester_offered"] = semesters_offered
                                normalized.setdefault("prerequisites", [])
                                normalized.setdefault("credits", 4)
                                normalized.setdefault("difficulty", 0)
                                normalized.setdefault("description", "")
                                math_courses.append(normalized)

    return math_courses


def get_available_courses_for_semester(
    completed_courses: List[str],
    target_semester: str,
    all_courses: Optional[List[Dict]] = None,
    major_name: Optional[str] = None,
) -> List[Dict]:
    """
    Get all available courses for a semester after applying all filters.

    This is the main orchestrator function that combines:
    1. Filtering out completed courses
    2. Filtering by prerequisites
    3. Filtering by semester availability
    4. Including applicable math courses

    Args:
        completed_courses: List of course codes the student has completed
        target_semester: Semester name like "Freshman Fall", "Sophomore Spring", etc.
        all_courses: Optional list of all course dictionaries from database.
                    If None, fetches from database.
        major_name: Optional major name to include major-specific math courses

    Returns:
        Combined list of available courses (DB courses + math courses) that:
        - Are not already completed
        - Have prerequisites satisfied
        - Are offered in the target semester
    """
    # Get all courses from DB if not provided
    if all_courses is None:
        all_courses = get_all_courses_from_db()

    # Debug: Check if database is empty
    if not all_courses:
        print("WARNING: No courses found in database. Make sure database is seeded.")
        return []

    # Step 1: Filter out completed courses
    available_courses = filter_completed_courses(all_courses, completed_courses)
    print(f"DEBUG: After filtering completed courses: {len(available_courses)} courses")

    # Step 2: Filter by prerequisites
    available_courses = filter_by_prerequisites(
        available_courses, completed_courses, all_courses
    )
    print(f"DEBUG: After filtering prerequisites: {len(available_courses)} courses")

    # Step 3: Filter by semester availability
    available_courses = filter_by_semester_availability(
        available_courses, target_semester
    )
    print(
        f"DEBUG: After filtering semester availability ({target_semester}): {len(available_courses)} courses"
    )

    # Step 4: Get math courses for the semester (if major is specified)
    math_courses = []
    if major_name:
        math_courses = _get_math_courses_for_semester(target_semester, major_name)
        print(f"DEBUG: Found {len(math_courses)} math courses for {major_name}")

        # Filter math courses: remove completed ones and check prerequisites
        completed_set = set(completed_courses)
        math_courses = [
            course
            for course in math_courses
            if course.get("course_code") not in completed_set
            and check_prerequisites_met(course, completed_courses, all_courses)
        ]
        print(f"DEBUG: After filtering math courses: {len(math_courses)} courses")

    # Step 5: Combine DB courses and math courses
    all_available_courses = available_courses + math_courses
    print(f"DEBUG: Total available courses: {len(all_available_courses)}")

    return all_available_courses
