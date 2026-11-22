from datetime import date, datetime, timezone
from decimal import Decimal

from bson.decimal128 import Decimal128
from pymongo.errors import DuplicateKeyError

from app.mongodb.collections import invoice_collection
from app.mongodb.document_schemas import InvoiceExtractionCreate


def normalize_text(value):
    """
    Normalize text for duplicate identification.
    """

    return " ".join(value.strip().upper().split())


def build_duplicate_identity(vendor):
    """
    Prefer GSTIN as vendor identity.
    Fall back to normalized vendor name.
    """

    gstin = vendor.get("gstin")

    if gstin:
        return f"GSTIN:{normalize_text(gstin)}"

    return f"NAME:{normalize_text(vendor['name'])}"


def convert_to_bson(value):

    if isinstance(value, Decimal):
        return Decimal128(str(value))

    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return datetime(
            value.year,
            value.month,
            value.day,
            tzinfo=timezone.utc
        )

    if isinstance(value, dict):

        return {
            key: convert_to_bson(item)
            for key, item in value.items()
        }

    if isinstance(value, list):

        return [
            convert_to_bson(item)
            for item in value
        ]

    return value


def register_invoice_extraction(invoice: InvoiceExtractionCreate):

    invoice_data = invoice.model_dump(mode="python")

    # Normalize invoice number
    invoice_data["invoice_number_normalized"] = normalize_text(
        invoice_data["invoice_number"]
    )

    # Normalize vendor identity
    vendor = invoice_data["vendor"]

    vendor["name_normalized"] = normalize_text(
        vendor["name"]
    )

    vendor["identity_key"] = build_duplicate_identity(vendor)

    if vendor.get("gstin"):
        vendor["gstin_normalized"] = normalize_text(
            vendor["gstin"]
        )

    # Convert Decimal and date values for MongoDB
    invoice_data = convert_to_bson(invoice_data)

    now = datetime.now(timezone.utc)

    invoice_data["created_at"] = now
    invoice_data["updated_at"] = now

    try:

        result = invoice_collection.insert_one(invoice_data)

        return result.inserted_id

    except DuplicateKeyError:

        raise ValueError(
            "Duplicate invoice detected. "
            "An invoice with this vendor identity "
            "and invoice number already exists."
        )


def get_invoice_extraction(invoice_id):

    return invoice_collection.find_one(
        {"_id": invoice_id}
    )


def update_extraction_status(invoice_id, new_status):

    allowed_statuses = {
        "PENDING",
        "COMPLETED",
        "VERIFIED",
        "FAILED"
    }

    if new_status not in allowed_statuses:

        raise ValueError("Invalid extraction status")

    result = invoice_collection.update_one(
        {"_id": invoice_id},
        {
            "$set": {
                "extraction.status": new_status,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

    return result