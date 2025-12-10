"""
test_user_model.py

Unit tests for user_model.py (create_user, verify_user, get_user_by_email, etc.).
Uses mongomock for in-memory MongoDB testing.
"""

import pytest
import bcrypt
from unittest.mock import patch, MagicMock
from mongomock import MongoClient

# pylint: disable=duplicate-code


@pytest.fixture
def mock_db():
    """Fixture to provide in-memory MongoDB via mongomock."""
    client = MongoClient()
    db = client["test_course_planner"]
    # Create unique index on email for students collection
    db.students.create_index("email", unique=True)
    yield db
    # Cleanup
    client.drop_database("test_course_planner")


@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return {
        "email": "student@nyu.edu",
        "password": "test_password_123",
        "name": "John Doe",
    }


class TestCreateUser:
    """Tests for create_user function."""

    def test_create_user_success(self, mock_db, sample_user):
        """Test successful user creation."""
        # Import inside test to use fixture
        import sys

        sys.path.insert(0, str(__file__).rsplit("tests", 1)[0])

        from api.user_model import create_user

        # Mock the db module-level variable
        with patch("api.user_model.db", mock_db):
            result = create_user(
                sample_user["email"], sample_user["password"], sample_user["name"]
            )

        assert result is not None
        assert result["email"] == sample_user["email"]
        assert result["name"] == sample_user["name"]
        assert result["netid"] == "student"
        assert "password" in result
        # Password should be hashed (not plaintext)
        assert result["password"] != sample_user["password"]

    def test_create_user_duplicate_email(self, mock_db, sample_user):
        """Test creating user with duplicate email returns None."""
        from api.user_model import create_user

        with patch("api.user_model.db", mock_db):
            # Create first user
            result1 = create_user(
                sample_user["email"], sample_user["password"], sample_user["name"]
            )
            assert result1 is not None

            # Try to create duplicate
            result2 = create_user(
                sample_user["email"], "different_password", "Different Name"
            )
            assert result2 is None

    def test_create_user_fields(self, mock_db, sample_user):
        """Test that user is created with all required fields."""
        from api.user_model import create_user

        with patch("api.user_model.db", mock_db):
            result = create_user(
                sample_user["email"], sample_user["password"], sample_user["name"]
            )

        # Check all expected fields exist
        expected_fields = [
            "name",
            "netid",
            "email",
            "password",
            "year",
            "major",
            "interests",
            "completed_courses",
            "planned_semesters",
        ]
        for field in expected_fields:
            assert field in result


class TestVerifyUser:
    """Tests for verify_user function."""

    def test_verify_user_success(self, mock_db, sample_user):
        """Test successful user verification."""
        from api.user_model import create_user, verify_user

        with patch("api.user_model.db", mock_db):
            # Create user
            create_user(
                sample_user["email"], sample_user["password"], sample_user["name"]
            )

            # Verify with correct password
            result = verify_user(sample_user["email"], sample_user["password"])

        assert result is not None
        assert result["email"] == sample_user["email"]

    def test_verify_user_wrong_password(self, mock_db, sample_user):
        """Test verification fails with wrong password."""
        from api.user_model import create_user, verify_user

        with patch("api.user_model.db", mock_db):
            create_user(
                sample_user["email"], sample_user["password"], sample_user["name"]
            )

            # Verify with wrong password
            result = verify_user(sample_user["email"], "wrong_password")

        assert result is None

    def test_verify_user_nonexistent(self, mock_db):
        """Test verification fails for non-existent user."""
        from api.user_model import verify_user

        with patch("api.user_model.db", mock_db):
            result = verify_user("nonexistent@nyu.edu", "any_password")

        assert result is None


class TestGetUserByEmail:
    """Tests for get_user_by_email function."""

    def test_get_user_by_email_success(self, mock_db, sample_user):
        """Test retrieving user by email."""
        from api.user_model import create_user, get_user_by_email

        with patch("api.user_model.db", mock_db):
            create_user(
                sample_user["email"], sample_user["password"], sample_user["name"]
            )
            result = get_user_by_email(sample_user["email"])

        assert result is not None
        assert result["email"] == sample_user["email"]

    def test_get_user_by_email_not_found(self, mock_db):
        """Test retrieving non-existent user returns None."""
        from api.user_model import get_user_by_email

        with patch("api.user_model.db", mock_db):
            result = get_user_by_email("nonexistent@nyu.edu")

        assert result is None


class TestUpdateUserProfile:
    """Tests for update_user_profile function."""

    def test_update_user_profile_success(self, mock_db, sample_user):
        """Test successful profile update."""
        from api.user_model import create_user, update_user_profile

        with patch("api.user_model.db", mock_db):
            create_user(
                sample_user["email"], sample_user["password"], sample_user["name"]
            )

            updates = {"major": "Computer Science", "year": "Sophomore"}
            result = update_user_profile(sample_user["email"], updates)

        assert result is True

    def test_update_user_profile_nonexistent(self, mock_db):
        """Test updating profile for non-existent user."""
        from api.user_model import update_user_profile

        with patch("api.user_model.db", mock_db):
            result = update_user_profile("nonexistent@nyu.edu", {"major": "CS"})

        assert result is False


class TestAddRemoveCompletedCourse:
    """Tests for add_completed_course and remove_completed_course."""

    def test_add_completed_course_success(self, mock_db, sample_user):
        """Test adding a completed course."""
        from api.user_model import create_user, add_completed_course

        with patch("api.user_model.db", mock_db):
            create_user(
                sample_user["email"], sample_user["password"], sample_user["name"]
            )
            result = add_completed_course(sample_user["email"], "CSCI-UA.0101")

        assert result is True

    def test_add_duplicate_completed_course(self, mock_db, sample_user):
        """Test adding duplicate completed course doesn't create duplicate."""
        from api.user_model import create_user, add_completed_course

        with patch("api.user_model.db", mock_db):
            create_user(
                sample_user["email"], sample_user["password"], sample_user["name"]
            )

            # Add course twice
            result1 = add_completed_course(sample_user["email"], "CSCI-UA.0101")
            result2 = add_completed_course(sample_user["email"], "CSCI-UA.0101")

        assert result1 is True
        assert result2 is True  # $addToSet prevents duplicates silently

    def test_remove_completed_course_success(self, mock_db, sample_user):
        """Test removing a completed course."""
        from api.user_model import (
            create_user,
            add_completed_course,
            remove_completed_course,
        )

        with patch("api.user_model.db", mock_db):
            create_user(
                sample_user["email"], sample_user["password"], sample_user["name"]
            )
            add_completed_course(sample_user["email"], "CSCI-UA.0101")

            result = remove_completed_course(sample_user["email"], "CSCI-UA.0101")

        assert result is True
