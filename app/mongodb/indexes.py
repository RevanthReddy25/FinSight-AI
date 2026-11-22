from app.mongodb.connection import mongodb

invoice_collection = mongodb["invoice_extractions"]


def create_invoice_indexes():

    # 1. Invoice number lookup
    invoice_collection.create_index(
        [("invoice_number", 1)],
        name="idx_invoice_number"
    )

    # 2. Vendor name lookup
    invoice_collection.create_index(
        [("vendor.name", 1)],
        name="idx_vendor_name"
    )

    # 3. Extraction status lookup
    invoice_collection.create_index(
        [("extraction.status", 1)],
        name="idx_extraction_status"
    )

    # 4. Vendor and invoice date lookup
    invoice_collection.create_index(
        [
            ("vendor.name", 1),
            ("invoice_date", -1)
        ],
        name="idx_vendor_invoice_date"
    )

    # 5. Duplicate invoice protection
    invoice_collection.create_index(
        [
            ("vendor.identity_key", 1),
            ("invoice_number_normalized", 1)
        ],
        unique=True,
        partialFilterExpression={
            "vendor.identity_key": {"$type": "string"},
            "invoice_number_normalized": {"$type": "string"}
        },
        name="unique_vendor_invoice"
    )

    print("All MongoDB indexes created successfully!")


def list_invoice_indexes():

    indexes = invoice_collection.list_indexes()

    print("\nAvailable indexes:")

    for index in indexes:
        print(index)