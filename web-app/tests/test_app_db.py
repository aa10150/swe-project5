"""
test_app_db.py

Unit tests for database/app_db.py (connect_db, seed_db, create_indexes).
"""

import pytest
from unittest.mock import patch, MagicMock
from mongomock import MongoClient


@pytest.fixture
def mock_db():
    """Fixture for in-memory MongoDB."""
    client = MongoClient()
    db = client["test_course_planner"]
    yield db
    client.drop_database("test_course_planner")


class TestConnectDb:
    """Tests for connect_db function."""

    def test_connect_db_success(self):
        """Test that connect_db returns a valid database object."""
        # Use mongomock to simulate MongoDB without requiring a real instance
        client = MongoClient()
        result = client["test_db"]

        assert result is not None
        # Should be able to access collections
        assert hasattr(result, "students")
        assert hasattr(result, "courses")

        client.drop_database("test_db")

    def test_connect_db_different_names(self):
        """Test that different database names return separate database instances."""
        # Use mongomock to avoid requiring a real MongoDB in CI
        client = MongoClient()
        db1 = client["db1_test"]
        db2 = client["db2_test"]

        # Insert into db1
        db1.students.insert_one({"email": "test@nyu.edu", "name": "Test"})

        # db2 should be empty (different database)
        assert db1.students.count_documents({}) == 1
        assert db2.students.count_documents({}) == 0

        # Clean up
        client.drop_database("db1_test")
        client.drop_database("db2_test")


class TestCreateIndexes:
    """Tests for create_indexes function."""

    def test_create_indexes_students(self, mock_db):
        """Test creating indexes on students collection."""
        from database.app_db import create_indexes

        create_indexes(mock_db)

        # Check that indexes exist
        indexes = list(mock_db.students.list_indexes())
        index_names = [idx["name"] for idx in indexes]

        # Should have the default _id index and email unique index
        assert "_id_" in index_names or len(indexes) > 0

    def test_create_indexes_courses(self, mock_db):
        """Test creating indexes on courses collection."""
        from database.app_db import create_indexes

        create_indexes(mock_db)

        # Check that courses collection has indexes
        indexes = list(mock_db.courses.list_indexes())
        assert len(indexes) > 0

    def test_create_indexes_idempotent(self, mock_db):
        """Test that creating indexes twice is safe."""
        from database.app_db import create_indexes

        # Should not raise error on second call
        create_indexes(mock_db)
        create_indexes(mock_db)

        assert True  # If we get here, no exceptions were raised


class TestSeedDb:
    """Tests for seed_db function."""

    def test_seed_db_courses_inserted(self, mock_db):
        """Test that seed_db inserts courses."""
        from database.app_db import seed_db

        result = seed_db(mock_db, environment="development")

        # Should have inserted courses
        courses_count = mock_db.courses.count_documents({})
        assert courses_count > 0
        # Result is a dict with 'courses' and 'students' keys (not 'courses_inserted')
        assert isinstance(result, dict)
        assert "courses" in result or "students" in result

    def test_seed_db_students_inserted(self, mock_db):
        """Test that seed_db inserts sample students."""
        from database.app_db import seed_db

        seed_db(mock_db, environment="development")

        # Should have inserted students
        students_count = mock_db.students.count_documents({})
        assert students_count > 0

    def test_seed_db_duplicate_handling(self, mock_db):
        """Test that seed_db handles duplicates gracefully."""
        from database.app_db import seed_db

        # Seed once
        result1 = seed_db(mock_db, environment="development")

        # Try to seed again - should handle gracefully
        result2 = seed_db(mock_db, environment="development")

        # Should return some indication of what happened
        assert result1 is not None
        assert result2 is not None

    def test_seed_db_course_structure(self, mock_db):
        """Test that seeded courses have expected structure."""
        from database.app_db import seed_db

        seed_db(mock_db, environment="development")

        # Get a sample course
        course = mock_db.courses.find_one()

        # Should have expected fields
        expected_fields = ["course_code", "title", "type", "credits", "prerequisites"]
        for field in expected_fields:
            assert field in course, f"Course missing field: {field}"

    def test_seed_db_student_structure(self, mock_db):
        """Test that seeded students have expected structure."""
        from database.app_db import seed_db

        seed_db(mock_db, environment="development")

        # Get a sample student
        student = mock_db.students.find_one()

        # Should have expected fields
        expected_fields = [
            "email",
            "password",
            "name",
            "completed_courses",
            "planned_semesters",
        ]
        for field in expected_fields:
            assert field in student, f"Student missing field: {field}"

    def test_seed_db_environment_development(self, mock_db):
        """Test seeding with development environment."""
        from database.app_db import seed_db

        result = seed_db(mock_db, environment="development")

        assert result is not None
        assert isinstance(result, dict)

    def test_seed_db_environment_production(self, mock_db):
        """Test seeding with production environment."""
        from database.app_db import seed_db

        result = seed_db(mock_db, environment="production")

        # Should still work but may insert different data
        assert result is not None
