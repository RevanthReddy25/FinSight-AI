import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import FinancialProject


@pytest.fixture
def client(tmp_path):

    # Create a separate temporary test database
    database_path = tmp_path / "test_finsight.db"

    test_engine = create_engine(
        URL.create(
            drivername="sqlite",
            database=str(database_path)
        ),
        connect_args={"check_same_thread": False}
    )

    # Create database tables
    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False
    )

    # Override the application's database dependency
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        test_engine.dispose()