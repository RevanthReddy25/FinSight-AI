from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import Vendor
from app.vendor_resolution import resolve_vendor

from app.mongodb.document_manager import (
    get_invoice_extraction
)

from app.mongodb.collections import invoice_collection


# --------------------------------------------------
# 1. RESOLVE MONGODB INVOICE VENDOR USING SQLITE
# --------------------------------------------------

def resolve_invoice_vendor(
    db: Session,
    invoice_id
):
    """
    Fetch an invoice from MongoDB and resolve
    its vendor using the SQLite vendor master.

    Returns resolution information.

    Does not commit the SQLite transaction.
    """

    # Fetch invoice from MongoDB

    invoice = get_invoice_extraction(invoice_id)

    if not invoice:

        raise ValueError(
            f"Invoice {invoice_id} was not found in MongoDB."
        )

    # Extract vendor information

    vendor_info = invoice.get("vendor", {})

    vendor_name = vendor_info.get("name")

    gstin = vendor_info.get("gstin")

    if not vendor_name:

        raise ValueError(
            "Invoice does not contain vendor information."
        )

    # Resolve vendor using existing resolution service

    vendor_id = resolve_vendor(
        db=db,
        vendor_name=vendor_name,
        gstin=gstin
    )

    # Determine resolution method

    if vendor_id:

        vendor = db.get(Vendor, vendor_id)

        if gstin:

            resolution_method = "GSTIN"

        else:

            resolution_method = "NORMALIZED_NAME"

        resolution_status = "RESOLVED"

        matched_vendor_name = vendor.vendor_name

    else:

        resolution_method = None

        resolution_status = (
            "REVIEW_REQUIRED"
            if gstin
            else "PENDING"
        )

        matched_vendor_name = None

    return {
        "invoice_id": str(invoice_id),

        "invoice_number": invoice.get(
            "invoice_number"
        ),

        "extracted_vendor_name": vendor_name,

        "extracted_gstin": gstin,

        "sql_vendor_id": vendor_id,

        "matched_vendor_name": matched_vendor_name,

        "resolution_status": resolution_status,

        "resolution_method": resolution_method
    }


# --------------------------------------------------
# 2. SAVE RESOLUTION RESULT IN MONGODB
# --------------------------------------------------

def save_invoice_vendor_resolution(
    invoice_id,
    resolution_result
):
    """
    Store vendor resolution metadata in MongoDB.

    Call this only after the SQLite transaction
    has been successfully committed.
    """

    update_data = {
        "vendor_resolution.status":
            resolution_result["resolution_status"],

        "vendor_resolution.method":
            resolution_result["resolution_method"],

        "vendor_resolution.resolved_at":
            datetime.now(timezone.utc),

        "updated_at":
            datetime.now(timezone.utc)
    }

    vendor_id = resolution_result["sql_vendor_id"]

    if vendor_id is not None:

        update_data["vendor.sql_vendor_id"] = vendor_id

        update_data[
            "vendor_resolution.matched_vendor_name"
        ] = resolution_result["matched_vendor_name"]

    else:

        update_data["vendor.sql_vendor_id"] = None

    result = invoice_collection.update_one(
        {"_id": invoice_id},
        {"$set": update_data}
    )

    if result.matched_count == 0:

        raise ValueError(
            "Invoice disappeared from MongoDB "
            "while saving vendor resolution."
        )

    return result