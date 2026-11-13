from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# 1. Define the project directory
BASE_DIR = Path(__file__).resolve().parent.parent


# 2. Define the SQLite database location
DATABASE_PATH = BASE_DIR / "finsight.db"


# 3. Create the database connection URL
DATABASE_URL = URL.create(
    drivername="sqlite",
    database=str(DATABASE_PATH)
)


# 4. Create the database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


# 5. Create a database session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# 6. Create the declarative base class
class Base(DeclarativeBase):
    pass


# 7. Database dependency for FastAPI
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()