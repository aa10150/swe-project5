"""
plan_utils.py

Utility functions for parsing and formatting course strings,
and managing semester plans in the database.
"""

import re
from typing import Dict, List, Optional


def parse_course_string(course_string: str) -> Optional[Dict]:
    """
    Parse a course string into structured format.

    Handles formats like:
    - "CSCI-UA.0101 Introduction to Computer Science (4 credits)"
    - "CSCI-UA 101 Intro to CS (4 credits)"
    - "MATH-UA.0121 Calculus I (4 credits)"

    Args:
        course_string: Course string in format "CODE Title (N credits)"

    Returns:
        Dictionary with course_code, title, credits, or None if parsing fails
    """
    if not course_string or not isinstance(course_string, str):
        return None

    # Pattern: "CODE Title (N credits)" or "CODE Title (N credit)"
    # Try to extract course code, title, and credits
    pattern = r"^([A-Z]+-UA\.?\d+)\s+(.+?)\s+\((\d+)\s+credits?\)$"
    match = re.match(pattern, course_string.strip())

    if match:
        course_code = match.group(1)
        title = match.group(2).strip()
        credit_hours = int(match.group(3))

        # Normalize course code format (handle spaces vs dots)
        course_code = course_code.replace(" ", ".")

        return {
            "course_code": course_code,
            "title": title,
            "credits": credit_hours,
        }

    # Fallback: try simpler pattern if credits format is different
    # Pattern: "CODE Title (N)" or just "CODE Title"
    pattern_simple = r"^([A-Z]+-UA\.?\d+)\s+(.+?)(?:\s+\((\d+)\))?$"
    match_simple = re.match(pattern_simple, course_string.strip())

    if match_simple:
        course_code = match_simple.group(1).replace(" ", ".")
        title = match_simple.group(2).strip()
        credit_hours = int(match_simple.group(3)) if match_simple.group(3) else 4

        return {
            "course_code": course_code,
            "title": title,
            "credits": credit_hours,
        }

    return None


def format_course_string(course: Dict) -> str:
    """
    Format a course dictionary into a string format.

    Args:
        course: Course dictionary with course_code, title, credits

    Returns:
        Formatted string like "CSCI-UA.0101 Introduction to Computer Science (4 credits)"
    """
    course_code = course.get("course_code", "UNKNOWN")
    title = course.get("title", course.get("name", "Unknown Course"))
    credit_hours = course.get("credits", 0)

    return f"{course_code} {title} ({credit_hours} credits)"


def update_semester_plan(
    user_email: str, semester: str, courses: List[str], db
) -> bool:
    """
    Update a user's semester plan in the database.

    Args:
        user_email: User's email
        semester: Semester name (e.g., "Freshman Fall")
        courses: List of course strings to save
        db: MongoDB database instance

    Returns:
        True if successful, False otherwise
    """
    try:
        # Parse course strings into structured format
        parsed_courses = []
        for course_str in courses:
            parsed = parse_course_string(course_str)
            if parsed:
                parsed_courses.append(parsed)

        # Get current user
        user = db.students.find_one({"email": user_email})
        if not user:
            return False

        # Get current planned_semesters
        planned_semesters = user.get("planned_semesters", [])

        # Find if semester already exists
        semester_index = None
        for idx, plan in enumerate(planned_semesters):
            if plan.get("semester") == semester:
                semester_index = idx
                break

        # Create semester plan entry
        semester_plan = {
            "semester": semester,
            "semester_index": _get_semester_index(semester),
            "courses": parsed_courses,
        }

        # Update or insert
        if semester_index is not None:
            planned_semesters[semester_index] = semester_plan
        else:
            planned_semesters.append(semester_plan)

        # Update in database
        db.students.update_one(
            {"email": user_email}, {"$set": {"planned_semesters": planned_semesters}}
        )

        return True
    except Exception as e:
        print(f"Error updating semester plan: {e}")
        return False


def get_semester_plan(user_email: str, semester: str, db) -> List[Dict]:
    """
    Get courses for a specific semester from user's plan.

    Args:
        user_email: User's email
        semester: Semester name
        db: MongoDB database instance

    Returns:
        List of course dictionaries, or empty list if not found
    """
    try:
        user = db.students.find_one({"email": user_email})
        if not user:
            return []

        planned_semesters = user.get("planned_semesters", [])
        for plan in planned_semesters:
            if plan.get("semester") == semester:
                return plan.get("courses", [])

        return []
    except Exception as e:
        print(f"Error getting semester plan: {e}")
        return []


def get_all_semester_plans(user_email: str, db) -> Dict[str, List[str]]:
    """
    Get all semester plans formatted for frontend.

    Args:
        user_email: User's email
        db: MongoDB database instance

    Returns:
        Dictionary mapping semester names to lists of course strings
        Format: { "Freshman Fall": ["CSCI-UA.0101 Intro to CS (4 credits)", ...], ... }
    """
    try:
        user = db.students.find_one({"email": user_email})
        if not user:
            return {}

        planned_semesters = user.get("planned_semesters", [])
        result = {}

        for plan in planned_semesters:
            semester = plan.get("semester")
            courses = plan.get("courses", [])
            # Format courses as strings
            course_strings = [format_course_string(course) for course in courses]
            result[semester] = course_strings

        return result
    except Exception as e:
        print(f"Error getting all semester plans: {e}")
        return {}


def _get_semester_index(semester: str) -> int:
    """
    Get semester index (0-7) from semester name.

    Args:
        semester: Semester name like "Freshman Fall"

    Returns:
        Index (0-7) or 0 if not found
    """
    semesters = [
        "Freshman Fall",
        "Freshman Spring",
        "Sophomore Fall",
        "Sophomore Spring",
        "Junior Fall",
        "Junior Spring",
        "Senior Fall",
        "Senior Spring",
    ]

    try:
        return semesters.index(semester)
    except ValueError:
        return 0
