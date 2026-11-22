from datetime import date
from decimal import Decimal
from uuid import uuid4

from app.mongodb.document_schemas import (
    InvoiceExtractionCreate,
    VendorInfo,
    InvoiceLineItem,
    InvoiceTotals,
    PaymentTerms,
    ExtractionInfo
)

from app.mongodb.document_manager import register_invoice_extraction
from app.mongodb.indexes import create_invoice_indexes


def main():

    # Create a unique invoice number for every execution.
    unique_invoice_number = f"DUP-TEST-{uuid4().hex[:8]}"

    invoice = InvoiceExtractionCreate(

        invoice_number=unique_invoice_number,

        vendor=VendorInfo(
            name="Duplicate Test Technologies"
        ),

        invoice_date=date(2026, 11, 21),

        currency="INR",

        line_items=[
            InvoiceLineItem(
                description="Software Services",
                quantity=Decimal("1"),
                unit_price=Decimal("10000"),
                line_total=Decimal("10000")
            )
        ],

        tax_breakdown=[],

        totals=InvoiceTotals(
            subtotal=Decimal("10000"),
            tax_total=Decimal("0"),
            grand_total=Decimal("10000")
        ),

        payment_terms=PaymentTerms(
            credit_days=30,
            payment_method="BANK_TRANSFER"
        ),

        extraction=ExtractionInfo(
            status="COMPLETED",
            method="MANUAL",
            model=None,
            confidence=1.0
        )
    )

    # Create indexes before inserting documents.
    create_invoice_indexes()

    # First insertion
    try:

        invoice_id = register_invoice_extraction(invoice)

        print("\nFirst insertion successful!")
        print("MongoDB ID:", invoice_id)

    except ValueError as error:

        print("First insertion failed:", error)
        return

    # Attempt duplicate insertion
    try:

        duplicate_id = register_invoice_extraction(invoice)

        print("ERROR: Duplicate invoice was accepted!")
        print("Duplicate ID:", duplicate_id)

    except ValueError as error:

        print("\nDuplicate prevention successful!")
        print(error)


if __name__ == "__main__":
    main()