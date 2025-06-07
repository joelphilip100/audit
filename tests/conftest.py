import pytest
import os

from fastapi.testclient import TestClient
from dotenv import load_dotenv
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from unittest.mock import MagicMock

from app.database import Base
from app.dependencies import get_db
from app.loggers import logger

from main import app

load_dotenv()

# Configuration based on environment variable
USE_PERSISTENT_TEST_DB = os.getenv("USE_PERSISTENT_TEST_DB", "false").lower() == "true"
db_path = Path(__file__).parent.parent / "db" / "test.db"
db_path.parent.mkdir(parents=True, exist_ok=True)
TEST_DATABASE_PATH = db_path.resolve()
TEST_DATABASE_URL = f"sqlite:///{TEST_DATABASE_PATH}"


@pytest.fixture(scope="module")
def test_engine():
    """Create test database engine - in-memory by default, file-based if specified"""
    if USE_PERSISTENT_TEST_DB:
        engine = create_engine(
            TEST_DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
    else:
        # Use in-memory database for testing
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,  # Keeps the in-memory db alive
        )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)

    yield engine

    # Clean up database
    Base.metadata.drop_all(bind=engine)
    if USE_PERSISTENT_TEST_DB and Path(TEST_DATABASE_PATH).exists():
        try:
            Path(TEST_DATABASE_PATH).unlink()
        except Exception as e:
            logger.warn(f"Warning: Could not delete test DB file - {e}")


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create a database session for each test with automatic rollback"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()  # Rollback any changes
        session.close()


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with database dependency override"""

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        # Clean up dependency overrides
        app.dependency_overrides.clear()


@pytest.fixture()
def fake_db():
    return MagicMock(spec=Session)
