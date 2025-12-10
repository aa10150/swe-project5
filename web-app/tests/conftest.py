"""
conftest.py

Shared pytest configuration and fixtures for the test suite.
Handles MONGO_URI setup before any modules are imported.
"""

import sys
import os

# Add the web-app directory to Python path
web_app_path = os.path.join(os.path.dirname(__file__), '..')
if web_app_path not in sys.path:
    sys.path.insert(0, web_app_path)

import pytest


def pytest_configure(config):
    """Configure pytest and set up environment variables BEFORE test collection."""
    # Set up environment variables required by the app
    os.environ['MONGO_URI'] = 'mongodb://localhost:27017'
    os.environ['MONGO_DB_NAME'] = 'test_course_planner'
    os.environ['ENVIRONMENT'] = 'testing'
    os.environ['FLASK_SECRET'] = 'test_secret_key'
    os.environ['WAIT_BEFORE_CONNECT'] = '0'


@pytest.fixture
def mock_db():
    """Provide a clean in-memory MongoDB for each test using mongomock."""
    from mongomock import MongoClient
    
    client = MongoClient()
    db = client['test_course_planner']
    
    yield db
    
    # Cleanup
    client.drop_database('test_course_planner')
