"""
llm_service.py

Module for generating course recommendations using OpenAI GPT-4.
"""

import json
import os
from typing import Dict, List, Optional

from openai import OpenAI


# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY not set in environment variables. "
        "Please set it in your .env file."
    )

client = OpenAI(api_key=OPENAI_API_KEY)


def _build_system_message() -> str:
    """
    Build the system message for the LLM.

    Returns:
        System message string defining the role and context
    """
    return """You are an expert academic advisor at NYU specializing in course planning and 
curriculum design. Your role is to help students create balanced, strategic course schedules 
that align with their academic goals, career aspirations, and major requirements.

You understand:
- NYU course structures, prerequisites, and difficulty levels
- Major requirement progressions and optimal sequencing
- Workload balancing and difficulty distribution
- Career path alignment with course selection
- Prerequisite chains and course dependencies

Provide thoughtful, personalized recommendations that consider the student's unique situation."""


def _format_course_for_prompt(course: Dict) -> str:
    """
    Format a course dictionary into a readable string for the prompt.

    Args:
        course: Course dictionary

    Returns:
        Formatted string with course information
    """
    course_code = course.get("course_code", "Unknown")
    title = course.get("title", course.get("name", "Unknown Title"))
    credits = course.get("credits", 0)
    difficulty = course.get("difficulty", 0)
    prerequisites = course.get("prerequisites", [])
    description = course.get("description", "")
    semester_offered = course.get("semester_offered", [])
    
    prereq_str = ", ".join(prerequisites) if prerequisites else "None"
    semester_str = ", ".join(semester_offered) if semester_offered else "Unknown"
    
    return f"""  - {course_code}: {title}
    Credits: {credits} | Difficulty: {difficulty}/5
    Prerequisites: {prereq_str}
    Offered: {semester_str}
    Description: {description[:200]}{"..." if len(description) > 200 else ""}"""


def _build_user_message(
    student_info: Dict,
    available_courses: List[Dict],
    major_requirements: Optional[Dict],
    major_progress: Optional[Dict],
    remaining_requirements: Optional[Dict],
    semester_info: Dict,
) -> str:
    """
    Build the user message with all context for course recommendations.

    Args:
        student_info: Dictionary with student profile (name, major, year, completed_courses, 
                     interests, career_path, side_interests)
        available_courses: List of available course dictionaries
        major_requirements: Major requirements dictionary (from major_requirements.py)
        major_progress: Major progress dictionary (from get_major_progress)
        remaining_requirements: Remaining requirements dictionary (from get_remaining_requirements)
        semester_info: Dictionary with semester name and target credits

    Returns:
        Formatted user message string
    """
    # Student profile section
    student_name = student_info.get("name", "Student")
    major = student_info.get("major", "Undeclared")
    year = student_info.get("year", "Unknown")
    completed_courses = student_info.get("completed_courses", [])
    interests = student_info.get("interests", [])
    career_path = student_info.get("career_path", "")
    side_interests = student_info.get("side_interests", [])
    
    # Semester info
    semester_name = semester_info.get("semester", "Unknown Semester")
    target_credits_min = semester_info.get("target_credits_min", 16)
    target_credits_max = semester_info.get("target_credits_max", 24)
    
    message = f"""Please recommend 4-6 courses for {student_name} for {semester_name}.

STUDENT PROFILE:
- Major: {major}
- Year: {year}
- Career Path: {career_path if career_path else "Not specified"}
- Interests: {", ".join(interests) if interests else "Not specified"}
- Side Interests: {", ".join(side_interests) if side_interests else "None"}
- Completed Courses: {", ".join(completed_courses) if completed_courses else "None"}

"""
    
    # Major requirements section
    if major_progress and "error" not in major_progress:
        progress_pct = major_progress.get("overall_progress", {}).get("percentage", 0)
        core_completed = major_progress.get("core_requirements", {}).get("count", 0)
        core_total = major_progress.get("core_requirements", {}).get("total", 0)
        elective_completed = len(major_progress.get("elective_requirements", {}).get("completed", []))
        elective_needed = major_progress.get("elective_requirements", {}).get("remaining_count", 0)
        
        message += f"""MAJOR PROGRESS:
- Overall Progress: {progress_pct}% complete
- Core Requirements: {core_completed}/{core_total} completed
- Electives: {elective_completed} completed, {elective_needed} still needed

"""
    
    # Remaining requirements section
    if remaining_requirements and "error" not in remaining_requirements:
        remaining_core = remaining_requirements.get("remaining_core", [])
        if remaining_core:
            message += "REMAINING CORE REQUIREMENTS:\n"
            for req in remaining_core[:5]:  # Limit to first 5 for brevity
                message += f"  - {req.get('course_code', '')}: {req.get('name', '')}\n"
            message += "\n"
        
        elective_info = remaining_requirements.get("remaining_electives", {})
        elective_count = elective_info.get("count_needed", 0)
        if elective_count > 0:
            message += f"ELECTIVES NEEDED: {elective_count} more required\n\n"
    
    # Available courses section
    message += f"AVAILABLE COURSES ({len(available_courses)} total):\n"
    for course in available_courses[:50]:  # Limit to first 50 courses for token efficiency
        message += _format_course_for_prompt(course) + "\n"
    
    if len(available_courses) > 50:
        message += f"\n... and {len(available_courses) - 50} more courses available.\n"
    
    # Instructions section
    message += f"""
RECOMMENDATION REQUIREMENTS:
1. Recommend 4-6 courses (aim for {target_credits_min}-{target_credits_max} total credits)
2. Balance difficulty: Mix easy (1-2), medium (3), and challenging (4-5) courses
3. Prioritize remaining core requirements if applicable
4. Align with career path: {career_path if career_path else "general academic growth"}
5. Consider side interests: {", ".join(side_interests) if side_interests else "none specified"}
6. Ensure all prerequisites are satisfied (already filtered, but double-check)
7. Consider course sequencing and logical progression

RESPONSE FORMAT:
Return a JSON object with this structure:
{{
  "courses": [
    {{
      "course_code": "CSCI-UA.0101",
      "title": "Introduction to Computer Science",
      "credits": 4,
      "reasoning": "Brief explanation of why this course is recommended"
    }},
    ...
  ]
}}

Provide thoughtful reasoning for each recommendation that considers the student's goals, 
progress, and the course's role in their academic journey."""
    
    return message

