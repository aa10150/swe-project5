"""
recommendation_routes.py

Flask blueprint for course recommendation API endpoints.
Requires JWT authentication.
"""

import os
from functools import wraps

import jwt
from flask import Blueprint, g, jsonify, request

from . import course_filtering, llm_service, major_requirements
from .user_model import db

recommendations = Blueprint("recommendations", __name__)

SECRET = os.getenv("JWT_SECRET", "defaultsecret")


def require_auth(f):
    """
    Decorator to require JWT authentication for a route.

    Extracts token from Authorization header, verifies it, and attaches
    the user to Flask's g object.

    Returns 401 if token is missing, invalid, or expired.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Unauthorized: Missing token"}), 401

        # Check for Bearer token format
        try:
            token = auth_header.split(" ")[1]  # "Bearer <token>"
        except IndexError:
            return jsonify({"error": "Unauthorized: Invalid token format"}), 401

        # Verify and decode token
        try:
            decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
            email = decoded.get("email")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Unauthorized: Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Unauthorized: Invalid token"}), 401

        # Fetch user from database
        if not email:
            return jsonify({"error": "Unauthorized: Invalid token payload"}), 401

        user = db.students.find_one({"email": email})
        if not user:
            return jsonify({"error": "Unauthorized: User not found"}), 401

        # Attach user to Flask's g object
        g.user = user

        return f(*args, **kwargs)

    return decorated_function


@recommendations.route("/generate", methods=["POST"])
@require_auth
def generate_recommendations():
    """
    Generate course recommendations for a semester.

    Requires JWT authentication.
    Request body:
    {
        "semester": "Freshman Fall",
        "career_path": "Software Engineering",
        "side_interests": ["Philosophy", "Music"]
    }

    Returns:
    {
        "courses": [
            {
                "course_code": "CSCI-UA.0101",
                "title": "Introduction to Computer Science",
                "credits": 4,
                "reasoning": "..."
            },
            ...
        ]
    }
    """
    # Get authenticated user
    user = g.user

    # Get request data
    data = request.json
    if not data:
        return jsonify({"error": "Missing request body"}), 400

    semester = data.get("semester")
    if not semester:
        return jsonify({"error": "Missing required field: semester"}), 400

    career_path = data.get("career_path", "")
    side_interests = data.get("side_interests", [])
    if not isinstance(side_interests, list):
        side_interests = []

    # Get user data
    completed_courses = user.get("completed_courses", [])
    major = user.get("major", "")
    year = user.get("year", "")
    interests = user.get("interests", [])
    name = user.get("name", "Student")

    # Get all courses from database
    all_courses = course_filtering.get_all_courses_from_db()

    # Get available courses for the semester
    available_courses = course_filtering.get_available_courses_for_semester(
        completed_courses=completed_courses,
        target_semester=semester,
        all_courses=all_courses,
        major_name=major if major else None,
    )

    if not available_courses:
        return (
            jsonify(
                {
                    "error": "No available courses found for this semester. "
                    "You may have completed all available courses or there are no courses "
                    "offered in this semester."
                }
            ),
            404,
        )

    # Get major requirements and progress (if major is specified)
    major_reqs = None
    major_progress = None
    remaining_reqs = None

    if major:
        major_reqs = major_requirements.get_major_requirements(major)
        major_progress = major_requirements.get_major_progress(
            major, completed_courses, all_courses
        )
        remaining_reqs = major_requirements.get_remaining_requirements(
            major, completed_courses, all_courses
        )

    # Build student info
    student_info = {
        "name": name,
        "major": major,
        "year": year,
        "completed_courses": completed_courses,
        "interests": interests,
        "career_path": career_path,
        "side_interests": side_interests,
    }

    # Build semester info
    semester_info = {
        "semester": semester,
        "target_credits_min": 16,
        "target_credits_max": 24,
    }

    # Generate recommendations using LLM
    recommended_courses = llm_service.generate_course_recommendations(
        student_info=student_info,
        available_courses=available_courses,
        major_requirements=major_reqs,
        major_progress=major_progress,
        remaining_requirements=remaining_reqs,
        semester_info=semester_info,
    )

    if not recommended_courses:
        return (
            jsonify(
                {"error": "Failed to generate recommendations. Please try again later."}
            ),
            500,
        )

    return jsonify({"courses": recommended_courses}), 200
