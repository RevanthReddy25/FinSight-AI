from bson import ObjectId

from app.database import SessionLocal

from app.invoice_vendor_service import (
    resolve_invoice_vendor,
    save_invoice_vendor_resolution
)


def main():

    # Replace this with an actual invoice _id
    # from your MongoDB Atlas collection.

    invoice_id = ObjectId(
        "6b009322e50c800b05c596d3"
    )

    db = SessionLocal()

    try:

        # Step 1: Resolve vendor using SQLite

        result = resolve_invoice_vendor(
            db=db,
            invoice_id=invoice_id
        )

        print("\nVendor resolution result:")

        for key, value in result.items():

            print(f"{key}: {value}")

        # Step 2: Commit SQLite changes

        db.commit()

        # Step 3: Save resolution metadata in MongoDB

        mongo_result = save_invoice_vendor_resolution(
            invoice_id=invoice_id,
            resolution_result=result
        )

        print(
            "\nMongoDB metadata updated:",
            mongo_result.modified_count
        )

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


if __name__ == "__main__":

    main()