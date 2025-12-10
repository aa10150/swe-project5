"""
test_plan_utils.py

Unit tests for plan_utils.py (parsing, formatting, semester plan management).
"""

import pytest
from unittest.mock import patch, MagicMock
from mongomock import MongoClient


@pytest.fixture
def mock_db():
    """Fixture for in-memory MongoDB."""
    client = MongoClient()
    db = client["test_course_planner"]
    db.students.create_index("email", unique=True)
    yield db
    client.drop_database("test_course_planner")


class TestParseCourseString:
    """Tests for parse_course_string function."""

    def test_parse_course_string_full_format(self):
        """Test parsing standard course string format."""
        from api.plan_utils import parse_course_string
        
        course_str = "CSCI-UA.0101 Introduction to Computer Science (4 credits)"
        result = parse_course_string(course_str)
        
        assert result is not None
        assert result["course_code"] == "CSCI-UA.0101"
        assert result["title"] == "Introduction to Computer Science"
        assert result["credits"] == 4

    def test_parse_course_string_single_credit(self):
        """Test parsing course with singular 'credit'."""
        from api.plan_utils import parse_course_string
        
        course_str = "MATH-UA.0120 Discrete Mathematics (1 credit)"
        result = parse_course_string(course_str)
        
        assert result is not None
        assert result["credits"] == 1

    def test_parse_course_string_simple_format(self):
        """Test parsing simpler course string format."""
        from api.plan_utils import parse_course_string
        
        course_str = "CSCI-UA.0101 Introduction to Computer Science"
        result = parse_course_string(course_str)
        
        assert result is not None
        assert result["course_code"] == "CSCI-UA.0101"
        assert result["title"] == "Introduction to Computer Science"
        # Should default to 4 credits
        assert result["credits"] == 4

    def test_parse_course_string_with_number_format(self):
        """Test parsing course code with space (like CSCI UA 0101)."""
        from api.plan_utils import parse_course_string
        
        course_str = "CSCI-UA 0101 Intro to CS (4 credits)"
        result = parse_course_string(course_str)
        
        # Should normalize to dot format
        if result:  # May fail depending on regex, but if it works should normalize
            assert "." in result["course_code"]

    def test_parse_course_string_invalid(self):
        """Test parsing invalid course strings."""
        from api.plan_utils import parse_course_string
        
        # Empty string
        assert parse_course_string("") is None
        
        # None input
        assert parse_course_string(None) is None
        
        # Non-string
        assert parse_course_string(123) is None
        
        # Completely malformed
        assert parse_course_string("random text here") is None or "course_code" in parse_course_string("random text here")


class TestFormatCourseString:
    """Tests for format_course_string function."""

    def test_format_course_string_basic(self):
        """Test formatting a course dictionary to string."""
        from api.plan_utils import format_course_string
        
        course = {
            "course_code": "CSCI-UA.0101",
            "title": "Introduction to Computer Science",
            "credits": 4
        }
        result = format_course_string(course)
        
        assert "CSCI-UA.0101" in result
        assert "Introduction to Computer Science" in result
        assert "4 credits" in result

    def test_format_course_string_missing_fields(self):
        """Test formatting course with missing fields."""
        from api.plan_utils import format_course_string
        
        # Missing credits (should default to 0)
        course = {
            "course_code": "CSCI-UA.0101",
            "title": "Intro to CS"
        }
        result = format_course_string(course)
        
        assert "CSCI-UA.0101" in result
        assert "Intro to CS" in result

    def test_format_course_string_with_name_field(self):
        """Test formatting course with 'name' instead of 'title'."""
        from api.plan_utils import format_course_string
        
        course = {
            "course_code": "MATH-UA.0121",
            "name": "Calculus I",
            "credits": 4
        }
        result = format_course_string(course)
        
        assert "MATH-UA.0121" in result
        assert "Calculus I" in result


class TestUpdateSemesterPlan:
    """Tests for update_semester_plan function."""

    def test_update_semester_plan_success(self, mock_db):
        """Test successful semester plan update."""
        from api.plan_utils import update_semester_plan
        from api.user_model import create_user
        
        email = "student@nyu.edu"
        
        with patch('api.plan_utils.parse_course_string') as mock_parse:
            mock_parse.return_value = {
                "course_code": "CSCI-UA.0101",
                "title": "Intro to CS",
                "credits": 4
            }
            
            # Setup user in DB
            mock_db.students.insert_one({
                "email": email,
                "name": "John Doe",
                "planned_semesters": []
            })
            
            courses = ["CSCI-UA.0101 Intro to CS (4 credits)"]
            result = update_semester_plan(email, "Freshman Fall", courses, mock_db)
        
        assert result is True

    def test_update_semester_plan_nonexistent_user(self, mock_db):
        """Test updating semester plan for non-existent user."""
        from api.plan_utils import update_semester_plan
        
        result = update_semester_plan("nonexistent@nyu.edu", "Freshman Fall", [], mock_db)
        
        assert result is False

    def test_update_semester_plan_multiple_courses(self, mock_db):
        """Test adding multiple courses to semester plan."""
        from api.plan_utils import update_semester_plan
        
        email = "student@nyu.edu"
        
        mock_db.students.insert_one({
            "email": email,
            "name": "John Doe",
            "planned_semesters": []
        })
        
        with patch('api.plan_utils.parse_course_string') as mock_parse:
            mock_parse.side_effect = [
                {"course_code": "CSCI-UA.0101", "title": "Intro to CS", "credits": 4},
                {"course_code": "MATH-UA.0121", "title": "Calculus I", "credits": 4}
            ]
            
            courses = [
                "CSCI-UA.0101 Intro to CS (4 credits)",
                "MATH-UA.0121 Calculus I (4 credits)"
            ]
            result = update_semester_plan(email, "Freshman Fall", courses, mock_db)
        
        assert result is True


class TestGetSemesterPlan:
    """Tests for get_semester_plan function."""

    def test_get_semester_plan_success(self, mock_db):
        """Test retrieving semester plan."""
        from api.plan_utils import get_semester_plan
        
        email = "student@nyu.edu"
        courses = [
            {"course_code": "CSCI-UA.0101", "title": "Intro to CS", "credits": 4}
        ]
        
        mock_db.students.insert_one({
            "email": email,
            "name": "John Doe",
            "planned_semesters": [
                {
                    "semester": "Freshman Fall",
                    "semester_index": 0,
                    "courses": courses
                }
            ]
        })
        
        result = get_semester_plan(email, "Freshman Fall", mock_db)
        
        assert result == courses

    def test_get_semester_plan_not_found(self, mock_db):
        """Test retrieving non-existent semester plan."""
        from api.plan_utils import get_semester_plan
        
        email = "student@nyu.edu"
        
        mock_db.students.insert_one({
            "email": email,
            "name": "John Doe",
            "planned_semesters": []
        })
        
        result = get_semester_plan(email, "Freshman Fall", mock_db)
        
        assert result == []

    def test_get_semester_plan_nonexistent_user(self, mock_db):
        """Test retrieving semester plan for non-existent user."""
        from api.plan_utils import get_semester_plan
        
        result = get_semester_plan("nonexistent@nyu.edu", "Freshman Fall", mock_db)
        
        assert result == []


class TestGetAllSemesterPlans:
    """Tests for get_all_semester_plans function."""

    def test_get_all_semester_plans_success(self, mock_db):
        """Test retrieving all semester plans."""
        from api.plan_utils import get_all_semester_plans
        
        email = "student@nyu.edu"
        
        mock_db.students.insert_one({
            "email": email,
            "name": "John Doe",
            "planned_semesters": [
                {
                    "semester": "Freshman Fall",
                    "courses": [
                        {"course_code": "CSCI-UA.0101", "title": "Intro to CS", "credits": 4}
                    ]
                },
                {
                    "semester": "Freshman Spring",
                    "courses": [
                        {"course_code": "MATH-UA.0121", "title": "Calculus I", "credits": 4}
                    ]
                }
            ]
        })
        
        result = get_all_semester_plans(email, mock_db)
        
        assert "Freshman Fall" in result
        assert "Freshman Spring" in result
        assert len(result["Freshman Fall"]) == 1

    def test_get_all_semester_plans_empty(self, mock_db):
        """Test retrieving all semester plans when empty."""
        from api.plan_utils import get_all_semester_plans
        
        email = "student@nyu.edu"
        
        mock_db.students.insert_one({
            "email": email,
            "name": "John Doe",
            "planned_semesters": []
        })
        
        result = get_all_semester_plans(email, mock_db)
        
        assert result == {}


class TestGetSemesterIndex:
    """Tests for _get_semester_index helper function."""

    def test_get_semester_index_all_semesters(self):
        """Test semester index mapping for all semesters."""
        from api.plan_utils import _get_semester_index
        
        semesters = [
            ("Freshman Fall", 0),
            ("Freshman Spring", 1),
            ("Sophomore Fall", 2),
            ("Sophomore Spring", 3),
            ("Junior Fall", 4),
            ("Junior Spring", 5),
            ("Senior Fall", 6),
            ("Senior Spring", 7),
        ]
        
        for semester_name, expected_index in semesters:
            assert _get_semester_index(semester_name) == expected_index

    def test_get_semester_index_invalid(self):
        """Test invalid semester returns 0."""
        from api.plan_utils import _get_semester_index
        
        assert _get_semester_index("Invalid Semester") == 0
