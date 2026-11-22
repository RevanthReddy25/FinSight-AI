from app.database import SessionLocal
from app.data_quality.report_generator import (
    generate_data_quality_report
)


def main():

    db = SessionLocal()

    try:
        report_path = generate_data_quality_report(
            db=db,
            output_path="reports/data_quality_report.md",
            include_mongodb=True
        )

        print("\nData quality report generated successfully!")
        print(f"Report location: {report_path}")

    except Exception as error:
        print("\nFailed to generate data quality report.")
        print("Error:", error)

        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()