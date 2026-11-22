from sqlalchemy import inspect, text
from app.database import engine


def migrate():

    inspector = inspect(engine)

    columns = [
        column["name"]
        for column in inspector.get_columns("import_batches")
    ]

    with engine.begin() as connection:

        if "uploaded_by_employee_id" not in columns:
            connection.execute(
                text("""
                    ALTER TABLE import_batches
                    ADD COLUMN uploaded_by_employee_id VARCHAR(50)
                """)
            )
            print("Added uploaded_by_employee_id")

        if "uploaded_from_device_id" not in columns:
            connection.execute(
                text("""
                    ALTER TABLE import_batches
                    ADD COLUMN uploaded_from_device_id VARCHAR(150)
                """)
            )
            print("Added uploaded_from_device_id")


if __name__ == "__main__":
    migrate()
    print("Database migration completed.")