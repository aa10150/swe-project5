"""
major_requirements.py

Flexible system for defining and checking major requirements across different majors.
Supports core requirements, electives, substitutions, and courses not in the database.
"""

from typing import Dict, List, Optional, Set, Union


# ============================================================================
# MAJOR REQUIREMENTS DEFINITIONS
# ============================================================================

# Math courses that may be referenced but not in the database
# These can be used in requirements and prerequisite checks
MATH_COURSES = {
    "MATH-UA.0009": "Precalculus",
    "MATH-UA.0120": "Discrete Mathematics",
    "MATH-UA.0121": "Calculus I",
    "MATH-UA.0122": "Calculus II",
    "MATH-UA.0131": "Math for Economics I",
    "MATH-UA.0140": "Linear Algebra",
    "MATH-UA.0185": "Probability and Statistics",
}


def get_major_requirements(major_name: str) -> Optional[Dict]:
    """
    Get major requirements for a given major.

    Args:
        major_name: Name of the major (e.g., "Computer Science")

    Returns:
        Dictionary containing major requirements structure, or None if major not found
    """
    major_name_lower = major_name.lower().strip()

    if major_name_lower == "computer science":
        return CS_MAJOR_REQUIREMENTS

    # Add other majors here as they are defined
    # if major_name_lower == "mathematics":
    #     return MATH_MAJOR_REQUIREMENTS

    return None


# ============================================================================
# COMPUTER SCIENCE MAJOR REQUIREMENTS
# ============================================================================

CS_MAJOR_REQUIREMENTS = {
    "major_name": "Computer Science",
    "total_courses_required": 12,
    "total_credits_required": 48,
    "min_gpa": 2.0,
    "min_grade": "C",
    "core_requirements": {
        "description": "7 core courses required",
        "courses": [
            {
                "course_code": "CSCI-UA.0101",
                "name": "Introduction to Computer Science",
                "semesters_offered": ["Fall", "Spring"],
                "prerequisites": [
                    "CSCI-UA.0002",
                    "CSCI-UA.0003",
                ],  # OR logic handled separately
                "notes": "Prerequisite: CSCI-UA.0002 or CSCI-UA.0003 or placement exam",
            },
            {
                "course_code": "CSCI-UA.0102",
                "name": "Data Structures",
                "semesters_offered": ["Fall", "Spring"],
                "prerequisites": ["CSCI-UA.0101"],
            },
            {
                "course_code": "CSCI-UA.0201",
                "name": "Computer Systems Organization",
                "semesters_offered": ["Fall", "Spring"],
                "prerequisites": ["CSCI-UA.0102"],
            },
            {
                "course_code": "CSCI-UA.0202",
                "name": "Operating Systems",
                "semesters_offered": ["Fall", "Spring"],
                "prerequisites": ["CSCI-UA.0201"],
            },
            {
                "course_code": "CSCI-UA.0310",
                "name": "Basic Algorithms",
                "semesters_offered": ["Fall", "Spring"],
                "prerequisites": ["CSCI-UA.0102"],
                "additional_requirements": [
                    "MATH-UA.0120",  # Discrete Mathematics
                    "MATH-UA.0121",  # Calculus I (OR MATH-UA.0131 Math for Economics I)
                ],
                "notes": "Also requires Discrete Mathematics and a Calculus course",
            },
            {
                "course_code": "MATH-UA.0121",
                "name": "Calculus I",
                "semesters_offered": ["Fall", "Spring", "Summer"],
                "prerequisites": ["MATH-UA.0009"],
                "is_math_course": True,  # Flag to indicate not in main DB
                "notes": "Prerequisite: MATH-UA.0009",
            },
        ],
    },
    "elective_requirements": {
        "description": "5 electives required",
        "count": 5,
        "type": "CSCI-UA.04xx",  # Pattern: courses numbered 0400-0499
        "substitutions": {
            "allowed": True,
            "max_count": 2,
            "courses": [
                {
                    "course_code": "MATH-UA.0122",
                    "name": "Calculus II",
                    "is_math_course": True,
                    "semesters_offered": ["Fall", "Spring", "Summer"],
                },
                {
                    "course_code": "MATH-UA.0140",
                    "name": "Linear Algebra",
                    "is_math_course": True,
                    "semesters_offered": ["Fall", "Spring"],
                },
                {
                    "course_code": "MATH-UA.0185",
                    "name": "Probability and Statistics",
                    "is_math_course": True,
                    "semesters_offered": ["Fall", "Spring"],
                },
            ],
        },
    },
    "notes": [
        "Only grades of 'C' or higher are applicable to the major",
        "Minimum GPA of 2.0 required",
        "Electives vary every fall and spring semester",
        "One elective option offered in summer semester",
    ],
}


# ============================================================================
# HELPER FUNCTIONS FOR REQUIREMENT CHECKING
# ============================================================================


def check_course_code_pattern(course_code: str, pattern: str) -> bool:
    """
    Check if a course code matches a pattern.

    Supports multiple pattern types:
    - Exact match: "CSCI-UA.0101"
    - Wildcard: "CSCI-UA.04xx" (matches 0400-0499)
    - Numeric comparison: "MATH-UA.0121+" (matches >= 0121)
    - Numeric comparison: "MATH-UA.0121-" (matches <= 0121)
    - Range: "MATH-UA.0120-0140" (matches 0120 to 0140 inclusive)

    Args:
        course_code: Course code to check (e.g., "CSCI-UA.0421", "MATH-UA.0125")
        pattern: Pattern to match (e.g., "CSCI-UA.04xx", "MATH-UA.0121+")

    Returns:
        True if course matches pattern
    """
    # Exact match
    if course_code == pattern:
        return True

    # Extract subject prefix and course number from course_code
    # Format: "SUBJECT-XX.NNNN" or "SUBJECT-XX.NNN"
    try:
        if "." not in course_code:
            return False

        course_prefix, course_num_str = course_code.rsplit(".", 1)

        # Try to extract numeric part
        try:
            course_num = int(course_num_str)
        except ValueError:
            # If not numeric, fall back to string matching
            course_num = None
    except Exception:
        return False

    # Pattern: "SUBJECT-XX.04xx" - wildcard matching
    if "xx" in pattern:
        pattern_prefix = pattern.replace("xx", "")
        return course_code.startswith(pattern_prefix) and len(course_code) == len(
            pattern
        )

    # Pattern: "SUBJECT-XX.NNNN+" - numeric >= comparison
    if pattern.endswith("+"):
        pattern_base = pattern[:-1]  # Remove the "+"
        if "." not in pattern_base:
            return False

        pattern_prefix, pattern_num_str = pattern_base.rsplit(".", 1)
        try:
            pattern_num = int(pattern_num_str)
            return (
                course_prefix == pattern_prefix
                and course_num is not None
                and course_num >= pattern_num
            )
        except ValueError:
            return False

    # Pattern: "SUBJECT-XX.NNNN-" - numeric <= comparison
    if pattern.endswith("-"):
        pattern_base = pattern[:-1]  # Remove the "-"
        if "." not in pattern_base:
            return False

        pattern_prefix, pattern_num_str = pattern_base.rsplit(".", 1)
        try:
            pattern_num = int(pattern_num_str)
            return (
                course_prefix == pattern_prefix
                and course_num is not None
                and course_num <= pattern_num
            )
        except ValueError:
            return False

    # Pattern: "SUBJECT-XX.NNNN-NNNN" - range matching
    if "-" in pattern and "." in pattern:
        # Check if it's a range (has both . and -)
        parts = pattern.split("-")
        if len(parts) == 2:
            start_pattern = parts[0]
            end_pattern = parts[1]

            # Extract start and end numbers
            if "." in start_pattern and "." in end_pattern:
                start_prefix, start_num_str = start_pattern.rsplit(".", 1)
                end_prefix, end_num_str = end_pattern.rsplit(".", 1)

                # Both should have same prefix
                if start_prefix != end_prefix:
                    return False

                try:
                    start_num = int(start_num_str)
                    end_num = int(end_num_str)
                    return (
                        course_prefix == start_prefix
                        and course_num is not None
                        and start_num <= course_num <= end_num
                    )
                except ValueError:
                    return False

    # Default: exact match (already checked at top, but return False for safety)
    return False


def get_completed_core_requirements(
    major_requirements: Dict, completed_courses: List[str]
) -> Dict[str, Union[List[str], int]]:
    """
    Get list of completed and remaining core requirements.

    Args:
        major_requirements: Major requirements dictionary
        completed_courses: List of course codes the student has completed

    Returns:
        Dictionary with 'completed' and 'remaining' lists, and 'count' of completed
    """
    completed = []
    remaining = []
    completed_set = set(completed_courses)

    core_reqs = major_requirements.get("core_requirements", {}).get("courses", [])

    for req in core_reqs:
        course_code = req["course_code"]
        if course_code in completed_set:
            completed.append(course_code)
        else:
            remaining.append(course_code)

    return {
        "completed": completed,
        "remaining": remaining,
        "count": len(completed),
        "total": len(core_reqs),
    }


def get_completed_electives(
    major_requirements: Dict,
    completed_courses: List[str],
    all_courses: Optional[List[Dict]] = None,
) -> Dict[str, Union[List[str], int]]:
    """
    Get list of completed electives that count toward major requirements.

    Args:
        major_requirements: Major requirements dictionary
        completed_courses: List of course codes the student has completed
        all_courses: Optional list of all course dictionaries from DB for pattern matching

    Returns:
        Dictionary with 'completed', 'remaining_count', and 'substitutions_used'
    """
    completed = []
    substitutions_used = []
    completed_set = set(completed_courses)

    elective_reqs = major_requirements.get("elective_requirements", {})
    pattern = elective_reqs.get("type", "")
    required_count = elective_reqs.get("count", 0)

    # Check regular electives (match pattern)
    if pattern and all_courses:
        for course in all_courses:
            course_code = course.get("course_code", "")
            if course_code in completed_set and check_course_code_pattern(
                course_code, pattern
            ):
                completed.append(course_code)

    # Check substitutions
    substitutions = elective_reqs.get("substitutions", {})
    if substitutions.get("allowed", False):
        substitution_courses = substitutions.get("courses", [])
        for sub_course in substitution_courses:
            course_code = sub_course.get("course_code", "")
            if course_code in completed_set:
                substitutions_used.append(course_code)
                completed.append(course_code)

    remaining_count = max(0, required_count - len(completed))

    return {
        "completed": completed,
        "remaining_count": remaining_count,
        "substitutions_used": substitutions_used,
        "max_substitutions": substitutions.get("max_count", 0) if substitutions else 0,
    }


def get_major_progress(
    major_name: str,
    completed_courses: List[str],
    all_courses: Optional[List[Dict]] = None,
) -> Dict:
    """
    Get overall progress toward completing major requirements.

    Args:
        major_name: Name of the major
        completed_courses: List of course codes the student has completed
        all_courses: Optional list of all course dictionaries from DB

    Returns:
        Dictionary with progress information including:
        - core_requirements: completed/remaining
        - electives: completed/remaining
        - overall_progress: percentage
    """
    major_reqs = get_major_requirements(major_name)

    if not major_reqs:
        return {"error": f"Major '{major_name}' not found", "major_name": major_name}

    core_status = get_completed_core_requirements(major_reqs, completed_courses)
    elective_status = get_completed_electives(
        major_reqs, completed_courses, all_courses
    )

    total_required = major_reqs.get("total_courses_required", 0)
    total_completed = core_status["count"] + len(elective_status["completed"])
    progress_percentage = (
        (total_completed / total_required * 100) if total_required > 0 else 0
    )

    return {
        "major_name": major_name,
        "core_requirements": core_status,
        "elective_requirements": elective_status,
        "overall_progress": {
            "completed": total_completed,
            "required": total_required,
            "percentage": round(progress_percentage, 2),
        },
    }


def get_remaining_requirements(
    major_name: str,
    completed_courses: List[str],
    all_courses: Optional[List[Dict]] = None,
) -> Dict:
    """
    Get list of remaining requirements for a major.

    Args:
        major_name: Name of the major
        completed_courses: List of course codes the student has completed
        all_courses: Optional list of all course dictionaries from DB

    Returns:
        Dictionary with remaining core and elective requirements
    """
    major_reqs = get_major_requirements(major_name)

    if not major_reqs:
        return {"error": f"Major '{major_name}' not found", "major_name": major_name}

    elective_status = get_completed_electives(
        major_reqs, completed_courses, all_courses
    )

    # Get remaining core courses with details
    remaining_core = []
    core_reqs = major_reqs.get("core_requirements", {}).get("courses", [])
    completed_set = set(completed_courses)

    for req in core_reqs:
        if req["course_code"] not in completed_set:
            remaining_core.append(
                {
                    "course_code": req["course_code"],
                    "name": req.get("name", ""),
                    "prerequisites": req.get("prerequisites", []),
                    "semesters_offered": req.get("semesters_offered", []),
                    "notes": req.get("notes", ""),
                }
            )

    # Get available electives that match pattern
    available_electives = []
    elective_reqs = major_reqs.get("elective_requirements", {})
    pattern = elective_reqs.get("type", "")

    if pattern and all_courses:
        completed_set = set(completed_courses)
        for course in all_courses:
            course_code = course.get("course_code", "")
            if course_code not in completed_set and check_course_code_pattern(
                course_code, pattern
            ):
                available_electives.append(
                    {
                        "course_code": course_code,
                        "name": course.get("title", ""),
                        "prerequisites": course.get("prerequisites", []),
                        "difficulty": course.get("difficulty", 0),
                        "credits": course.get("credits", 0),
                    }
                )

    return {
        "major_name": major_name,
        "remaining_core": remaining_core,
        "remaining_electives": {
            "count_needed": elective_status["remaining_count"],
            "available_courses": available_electives,
            "substitutions_available": elective_reqs.get("substitutions", {}).get(
                "courses", []
            ),
        },
    }


def is_math_course(course_code: str) -> bool:
    """
    Check if a course code is a math course (not in main database).

    Args:
        course_code: Course code to check

    Returns:
        True if course is a math course
    """
    return course_code in MATH_COURSES


def get_math_course_info(course_code: str) -> Optional[Dict]:
    """
    Get information about a math course.

    Args:
        course_code: Math course code

    Returns:
        Dictionary with course info or None if not found
    """
    if course_code not in MATH_COURSES:
        return None

    return {
        "course_code": course_code,
        "name": MATH_COURSES[course_code],
        "is_math_course": True,
        "subject": "MATH-UA",
    }
