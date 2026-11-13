from app.database import Base, engine
from app.models import FinancialProject


def create_tables():
    """Create all registered database tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    create_tables()