import pytest

from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Import models to register their tables
from app.models import (
    FinancialProject,
    FinancialTransaction,
    Vendor,
    Category,
    UnresolvedVendor,
    ImportBatch,
    RejectedTransaction
)


@pytest.fixture
def test_engine():

    # Shared isolated in-memory SQLite database
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    Base.metadata.create_all(bind=engine)

    yield engine

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def TestingSessionLocal(test_engine):

    return sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False
    )


@pytest.fixture
def db_session(TestingSessionLocal):

    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()


@pytest.fixture
def client(TestingSessionLocal):

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