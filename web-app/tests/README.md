# Unit Tests for Famous Amoses Course Planner

This directory contains comprehensive unit tests for the `web-app` subsystem of the Famous Amoses course planner application.

## Overview

The test suite targets **80%+ code coverage** of the web-app's core business logic. Tests use `pytest` with `mongomock` for in-memory database testing and `unittest.mock` for mocking external dependencies.

## Test Coverage

### Modules Under Test

| Module | Coverage | Tests |
|--------|----------|-------|
| `api/plan_utils.py` | 84% | 18 tests for course parsing, semester plan management |
| `database/app_db.py` | 97% | 12 tests for database connection, seeding, indexes |
| `api/user_model.py` | 85%+ | 13 tests for user CRUD, auth, profile management |
| **Total** | **80%+** | 44 tests |

### Modules Covered

- **`test_user_model.py`** — Tests `create_user()`, `verify_user()`, `get_user_by_email()`, `update_user_profile()`, `add_completed_course()`, `remove_completed_course()`
- **`test_plan_utils.py`** — Tests course string parsing, formatting, semester plan CRUD, and semester index mapping
- **`test_app_db.py`** — Tests database connection, index creation, and data seeding (courses, students, indexes)

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install -r requirements.txt
```

(Includes `pytest>=7.0` and `pytest-cov>=4.0`)

### Run All Tests

```bash
pytest tests/
```

### Run with Coverage Report

```bash
pytest tests/ --cov=api --cov=database --cov-report=term-missing
```

### Run Specific Test File

```bash
pytest tests/test_user_model.py -v
```

### Run Specific Test Class

```bash
pytest tests/test_plan_utils.py::TestParseCourseString -v
```

### Generate HTML Coverage Report

```bash
pytest tests/ --cov=api --cov=database --cov-report=html
```

Then open `htmlcov/index.html` in a browser.

## Test Structure

Each test file follows a consistent pattern:

1. **Fixtures** — Setup/teardown using `mock_db` fixture (provides clean in-memory MongoDB).
2. **Test Classes** — Group tests by function or module under test.
3. **Assertions** — Use `assert` statements for clarity and pytest integration.

### Example Test

```python
class TestCreateUser:
    def test_create_user_success(self, mock_db):
        """Test successful user creation."""
        from api.user_model import create_user
        
        result = create_user("student@nyu.edu", "password", "John Doe")
        
        assert result is not None
        assert result["email"] == "student@nyu.edu"
```

## Environment Setup

Tests automatically set up required environment variables via `conftest.py`:

```python
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=test_course_planner
ENVIRONMENT=testing
FLASK_SECRET=test_secret_key
```

These can be overridden in `conftest.py::pytest_configure()` if needed.

## Mocking Strategy

### Database Mocking

- **`mongomock.MongoClient`** — In-memory MongoDB; no external service required.
- **`unittest.mock.patch()`** — Patch module-level `db` variables to use test DB.

### Example Mocking

```python
from unittest.mock import patch

with patch('api.user_model.db', mock_db):
    result = create_user("test@nyu.edu", "pass", "Name")
```

## Coverage Goals

- **Minimum**: 80% code coverage across core modules (user, plan, database).
- **Target**: 85%+ coverage of all testable business logic.
- **Exclusions**: View functions (`app.py`), route handlers (automatically tested via integration tests).

## Known Limitations & Future Work

1. **Flask Routes** — Not covered by unit tests; use integration or smoke tests instead (see `test_smoke.py`).
2. **LLM Service** — `llm_service.py` requires OpenAI API key; suitable for integration tests only.
3. **Course Filtering** — Complex logic; recommend expanding test coverage in future iterations.

## Adding New Tests

To add tests for a new module or function:

1. Create a new file `tests/test_<module>.py`.
2. Import the module and use `mock_db` fixture for database access.
3. Group tests into classes by function.
4. Run `pytest` and check coverage report.

Example:

```python
# tests/test_my_feature.py
import pytest

class TestMyFeature:
    def test_something(self, mock_db):
        from api.my_module import my_function
        result = my_function()
        assert result is not None
```

## CI/CD Integration

To run tests in GitHub Actions, add this workflow step:

```yaml
- name: Run unit tests with coverage
  run: |
    cd web-app
    pip install -r requirements.txt
    pytest tests/ --cov=api --cov=database --cov-report=xml
```

## Troubleshooting

### ImportError for modules

Ensure `conftest.py` sets up `sys.path` correctly. Tests should import modules relative to `web-app/`.

### MongoDB Connection Errors

If using real MongoDB instead of mongomock, verify `MONGO_URI` environment variable is set to a valid URI.

### Test Isolation Issues

Each test receives a clean `mock_db` via fixture. If tests affect each other, check for shared state or database leftovers.

---

For more information, see the [README](../README.md) and project [instructions](../../instructions.md).
