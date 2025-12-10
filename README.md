# Final Project

An exercise to put to practice software development teamwork, subsystem communication, containers, deployment, and CI/CD pipelines. See [instructions](./instructions.md) for details.

# NYU CS & Math Course Planner

A course recommender designed to help a Computer Science or Math student at NYU create a four-year plan by using an LLM to suggest courses from the CAS catalog that fulfill their requirements and classes relevant to their interests.

[![log github events](https://github.com/swe-students-fall2025/5-final-famous-amoses/actions/workflows/event-logger.yml/badge.svg)](https://github.com/swe-students-fall2025/5-final-famous-amoses/actions/workflows/event-logger.yml)
[![Web App Subsystem CI](https://github.com/swe-students-fall2025/5-final-famous-amoses/actions/workflows/test-api-subsystem.yml/badge.svg)](https://github.com/swe-students-fall2025/5-final-famous-amoses/actions/workflows/test-api-subsystem.yml)
[![Database Subsystem CI](https://github.com/swe-students-fall2025/5-final-famous-amoses/actions/workflows/test-database-subsystem.yml/badge.svg)](https://github.com/swe-students-fall2025/5-final-famous-amoses/actions/workflows/test-database-subsystem.yml)

## Container Images

This project uses the following custom container images, hosted on Docker Hub:

- Web application: [`jwn7470/web-app`](https://hub.docker.com/r/jwn7470/web-app)

The application also depends on the official MongoDB image:

- Database: [`mongo:7`](https://hub.docker.com/_/mongo)

## Team Members

- **Frontend:** [Anshu Aramandla](https://github.com/aa10150)
- **Backend (LLM/recommendation):** [Apoorv Belgundi](https://github.com/apoorvib)
- **Backend (CRUD operations):** [Harrison Coon](https://github.com/hoc2006-code)
- **DB Setup & Login:** [Kylie Lin](https://github.com/kylin1209)
- **Docker & Integration:** [Jacob Ng](https://github.com/jng20)

## Instructions

### Environment variables

Create a file at `web-app/.env` by copying `web-app/.env.example` and filling in values appropriate for your environment. Do not commit production secrets to version control — only commit `web-app/.env.example` with dummy/example values.

Example `web-app/.env` (copy into `web-app/.env` and edit):

```text
MONGO_URI = mongodb://mongo:27017/course_planner
MONGO_DB_NAME = course_planner
ENVIRONMENT = development
WAIT_BEFORE_CONNECT = 2
OPENAI_API_KEY = sk-proj
```

- `MONGO_URI`: MongoDB connection string. When using Docker Compose, `mongodb://mongo:27017` points to the `mongo` service in `docker-compose.yml`.
- `MONGO_DB_NAME`: name of the database used by the app.
- `WAIT_BEFORE_CONNECT`: seconds the seeder will wait before attempting a DB connection (helps when starting containers together).
- `ENVIRONMENT`: `development` or `production` — controls seeding/debug behavior.
- `FLASK_SECRET`: secret key for Flask session management. Keep this private in production.

If additional secrets/configuration files are required, include an example file (for example `web-app/.env.example`) and document exact steps for creating the real file(s) with the course admins.

### Running the Webapp

You can run the app with Docker Compose (recommended) or directly in a local Python environment.

Run with Docker Compose (recommended)

1. Copy the example environment file and edit it as needed:

```bash
cp web-app/.env.example web-app/.env
# edit web-app/.env as needed
```

2. Build and start the services:

```bash
docker-compose up --build
```

3. Open `http://127.0.0.1:5000` in your browser.

Notes:

- The `web` container runs `start.sh`, which attempts to seed the database (`python -m database.seed`) before starting the Flask app. If the database is already seeded, the script will warn and continue.
- To run the seeder manually while containers are running:

```bash
docker-compose run --rm web python -m database.seed
```

Run locally without Docker (optional)

1. From the repository root, change into `web-app`, create and activate a virtual environment, and install dependencies:

```bash
cd web-app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Ensure `web-app/.env` points to your MongoDB instance and seed the DB:

```bash
python -m database.seed
```

3. Start the Flask server:

```bash
python run.py
```

4. Open `http://localhost:5000` to verify the app is running.

Stopping

- If started with Docker Compose: `docker-compose down`.
- If started locally: stop the server (Ctrl+C) and run `deactivate` to exit the virtual environment.

## Testing

The `web-app` subsystem includes a comprehensive unit test suite targeting **80%+ code coverage** of core business logic.

### Test Suite Overview

- **44 unit tests** covering user management, course parsing, semester planning, and database operations
- **Coverage by module**:
  - `api/plan_utils.py`: 84%
  - `api/user_model.py`: 80%
  - `database/app_db.py`: 97%
- **Testing framework**: pytest with mongomock for in-memory database testing

### Running Tests

Install test dependencies (included in `web-app/requirements.txt`):

```bash
cd web-app
pip install -r requirements.txt
```

Run all tests:

```bash
pytest tests/
```

Run tests with coverage report:

```bash
pytest tests/ --cov=api --cov=database --cov-report=term-missing
```

Generate HTML coverage report:

```bash
pytest tests/ --cov=api --cov=database --cov-report=html
```

Then open `htmlcov/index.html` in a browser.

### Test Structure

Tests are organized by module in `web-app/tests/`:

- **`test_user_model.py`** — User CRUD, authentication, profile management (13 tests)
- **`test_plan_utils.py`** — Course parsing, formatting, semester plan operations (18 tests)
- **`test_app_db.py`** — Database connection, seeding, indexing (12 tests)
- **`conftest.py`** — Shared pytest fixtures and environment setup
- **`README.md`** — Detailed testing documentation
