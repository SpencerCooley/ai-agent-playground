import sys
import os

# Add the /app directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from main import app
from dependencies.dependencies import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config
from sqlalchemy.exc import ProgrammingError
from models.base import Base  # Import your SQLAlchemy models
from sqlalchemy import text
from pydantic import ConfigDict

# Use test database
os.environ["DATABASE_URL"] = "postgresql://test_user:test_password@test_db:5432/test_db"

# Create test database engine
TEST_DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Reset database before running tests
def reset_database():
    """Ensure database is fully reset before running migrations, including dropping all ENUM types."""
    alembic_cfg = Config("alembic.ini")

    with engine.connect() as connection:
        connection.execution_options(isolation_level="AUTOCOMMIT")

        # Fetch all ENUM types in the current database
        result = connection.execute(text(
            "SELECT typname FROM pg_type WHERE typtype = 'e';"
        ))

        # Drop each ENUM type found
        for row in result:
            enum_name = row[0]
            try:
                connection.execute(text(f"DROP TYPE IF EXISTS {enum_name} CASCADE;"))
                print(f"Dropped ENUM type: {enum_name}")
            except ProgrammingError:
                pass  # Ignore if it fails

    # Rollback to base (clean state)
    command.downgrade(alembic_cfg, "base")

    # Apply all migrations again
    command.upgrade(alembic_cfg, "head")

# Override FastAPI's get_db() dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Drops the test database, applies migrations before running tests, and cleans up afterward."""
    reset_database()  # Drop and recreate the test database
    yield  # Run tests
    reset_database()  # Reset again after tests

@pytest.fixture(scope="function")
def db():
    """Creates a new database session for each test."""
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="function")
def client():
    """FastAPI TestClient using the test database."""
    return TestClient(app)
