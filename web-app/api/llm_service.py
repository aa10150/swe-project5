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
    print("WARNING: OPENAI_API_KEY not set in environment variables.")
    print(
        "LLM recommendations will not work. Please set OPENAI_API_KEY in your .env file."
    )
    client = None
else:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"ERROR: Failed to initialize OpenAI client: {e}")
        client = None


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
- **MAJOR: {major}** (CRITICAL: All recommendations must align with this major)
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
        elective_completed = len(
            major_progress.get("elective_requirements", {}).get("completed", [])
        )
        elective_needed = major_progress.get("elective_requirements", {}).get(
            "remaining_count", 0
        )

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
    for course in available_courses[
        :50
    ]:  # Limit to first 50 courses for token efficiency
        message += _format_course_for_prompt(course) + "\n"

    if len(available_courses) > 50:
        message += f"\n... and {len(available_courses) - 50} more courses available.\n"

    # Instructions section - REORDERED AND EMPHASIZED
    message += f"""
CRITICAL RECOMMENDATION PRIORITIES (in order of importance):
1. MAJOR ALIGNMENT (HIGHEST PRIORITY):
   The student's major is: "{major}"
   CRITICAL: Strongly prioritize courses that align with the student's declared major.
   - If major is "Computer Science": Prioritize CS courses (CSCI-UA courses) that fulfill major requirements.
     Focus on core CS requirements first, then CS electives that support the career path.
   - If major is "Mathematics": Prioritize Math courses (MATH-UA courses) that fulfill major requirements.
     Focus on core Math requirements first, then Math electives that support the career path.
   - If major is not specified or "Undeclared": Still consider major requirements if available, but balance with other factors.
   The student MUST complete their major requirements to graduate. Major alignment is more important than general interests.
   NOTE: It is acceptable to include courses from other majors/departments (e.g., Math courses for CS majors, CS courses for Math majors)
   when they directly support the student's interests or career path, AS LONG AS major requirements are still being prioritized and completed.

2. CAREER PATH ALIGNMENT (HIGH PRIORITY): 
   The student's intended career path is: "{career_path if career_path else "Not specified"}"
   Within the context of the student's major, prioritize courses that directly support this career path.
   For example:
   - If career path is "Software Engineering" and major is CS: prioritize Software Engineering, Web Development, 
     Database Design, Agile/DevOps, Applied Internet Technology, etc.
   - If career path is "AI/ML" or "Machine Learning" and major is CS: prioritize Predictive Analytics, 
     Data Management, Big Data Processing, Machine Learning, Deep Learning, etc.
   - If career path is "Data Science" and major is CS: prioritize Database Design, Predictive Analytics, 
     Data Management, Probability and Statistics, etc.
   - If career path is "Systems" and major is CS: prioritize Operating Systems, Computer Systems Organization, 
     Theory of Computation, etc.
   - If career path is "Cybersecurity" and major is CS: prioritize Introduction to Cryptography, etc.
   DO NOT recommend generic courses when career-specific courses within the major are available.

3. SIDE INTERESTS (MEDIUM PRIORITY):
   The student has expressed interest in: {", ".join(side_interests) if side_interests else "none specified"}
   Include 1-2 courses that align with these side interests to create a well-rounded schedule.
   IMPORTANT: If an interest requires courses from another major/department, DO NOT hesitate to recommend them.
   For example:
   - If interest is "Machine Learning" or "AI": Recommend relevant Math courses like Probability and Statistics (MATH-UA.0185),
     Linear Algebra (MATH-UA.0140), or Theory of Probability (MATH-UA.0333) even if the student is a CS major.
   - If interest is "Data Science": Recommend Math courses like Probability and Statistics, Linear Algebra, etc.
   - If interest is "Cryptography": Recommend relevant Math courses that support cryptography.
   - Cross-major courses that support interests are valuable and should be included when they directly support the interest.
   However, ensure that major requirements are still being prioritized and completed. Balance is key:
   prioritize major requirements first, but include cross-major courses when they directly support stated interests.
   If side interests are specified, make sure at least one recommended course connects to them.

4. Major Requirements: Prioritize remaining core requirements if applicable (already covered in priority #1)
5. Difficulty Balance: Mix easy (1-2), medium (3), and challenging (4-5) courses
6. Course Sequencing: Ensure logical progression and prerequisite satisfaction

IMPORTANT CONSTRAINTS:
- DO NOT recommend courses the student has already completed: {", ".join(completed_courses) if completed_courses else "None"}
- DO NOT recommend courses already planned for ANY semester (including previous semesters)
- The available courses list has already been filtered to exclude completed and planned courses
- Recommend 4-6 courses (aim for {target_credits_min}-{target_credits_max} total credits)
- All prerequisites are already satisfied (already filtered, but double-check)

RESPONSE FORMAT:
Return a JSON object with this structure:
{{
  "courses": [
    {{
      "course_code": "CSCI-UA.0101",
      "title": "Introduction to Computer Science",
      "credits": 4,
      "reasoning": "Brief explanation that specifically mentions how this course aligns with the career path '{career_path if career_path else "academic goals"}' and/or side interests {side_interests if side_interests else "general academic growth"}"
    }},
    ...
  ]
}}

Provide thoughtful reasoning for each recommendation that explicitly connects the course to the student's career path and interests. 
Each reasoning should clearly state WHY this course is relevant to their career goals and how it fits into their academic journey."""

    return message


def generate_course_recommendations(
    student_info: Dict,
    available_courses: List[Dict],
    major_requirements: Optional[Dict],
    major_progress: Optional[Dict],
    remaining_requirements: Optional[Dict],
    semester_info: Dict,
) -> Optional[List[Dict]]:
    """
    Generate course recommendations using OpenAI GPT-4.

    Args:
        student_info: Dictionary with student profile (name, major, year, completed_courses,
                     interests, career_path, side_interests)
        available_courses: List of available course dictionaries (already filtered)
        major_requirements: Major requirements dictionary (from major_requirements.py)
        major_progress: Major progress dictionary (from get_major_progress)
        remaining_requirements: Remaining requirements dictionary (from get_remaining_requirements)
        semester_info: Dictionary with semester name and target credits

    Returns:
        List of recommended course dictionaries with structure:
        [{"course_code": "...", "title": "...", "credits": 4, "reasoning": "..."}, ...]
        Returns None if API call fails or response is invalid
    """
    # Check if OpenAI client is initialized
    if client is None:
        print("ERROR: OpenAI client not initialized. OPENAI_API_KEY may be missing.")
        return None

    try:
        # Build messages
        system_message = _build_system_message()
        user_message = _build_user_message(
            student_info,
            available_courses,
            major_requirements,
            major_progress,
            remaining_requirements,
            semester_info,
        )

        print(
            f"DEBUG: Calling OpenAI API with {len(available_courses)} available courses"
        )

        # Use a model that supports JSON mode
        # gpt-4-turbo, gpt-4o, or gpt-3.5-turbo support JSON mode
        # gpt-4 (base) does NOT support JSON mode
        model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")

        # Call OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,  # Balance between creativity and consistency
        )

        # Extract response content
        response_content = response.choices[0].message.content
        if not response_content:
            print("ERROR: OpenAI API returned empty response")
            return None

        # Parse JSON response
        try:
            response_data = json.loads(response_content)
        except json.JSONDecodeError as e:
            print(
                f"ERROR: Failed to parse JSON response. Raw response: {response_content[:500]}"
            )
            # Try to extract JSON from markdown code blocks if present
            if "```json" in response_content:
                json_start = response_content.find("```json") + 7
                json_end = response_content.find("```", json_start)
                if json_end != -1:
                    response_content = response_content[json_start:json_end].strip()
                    response_data = json.loads(response_content)
                else:
                    raise ValueError("Invalid JSON response format") from e
            elif "```" in response_content:
                # Try to extract from generic code block
                json_start = response_content.find("```") + 3
                json_end = response_content.find("```", json_start)
                if json_end != -1:
                    response_content = response_content[json_start:json_end].strip()
                    response_data = json.loads(response_content)
                else:
                    raise ValueError("Invalid JSON response format") from e
            else:
                raise ValueError(f"Failed to parse JSON response: {e}") from e

        # Extract courses from response
        courses = response_data.get("courses", [])

        if not courses:
            print("WARNING: OpenAI API returned no courses in response")
            return None

        # Validate course structure
        validated_courses = []
        for course in courses:
            if isinstance(course, dict) and "course_code" in course:
                validated_courses.append(
                    {
                        "course_code": course.get("course_code", ""),
                        "title": course.get("title", ""),
                        "credits": course.get("credits", 0),
                        "reasoning": course.get("reasoning", ""),
                    }
                )

        if not validated_courses:
            print("WARNING: No valid courses found in OpenAI response")
            return None

        print(
            f"DEBUG: Successfully generated {len(validated_courses)} course recommendations"
        )
        return validated_courses

    except Exception as e:
        # Log error with full traceback
        print(f"ERROR generating course recommendations: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return None
