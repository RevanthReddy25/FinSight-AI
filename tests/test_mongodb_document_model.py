from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

from bson.decimal128 import Decimal128

from app.mongodb.document_schemas import (
    InvoiceExtractionCreate,
    VendorInfo,
    InvoiceLineItem,
    TaxComponent,
    InvoiceTotals,
    PaymentTerms,
    ExtractionInfo,
)

from app.mongodb import document_manager


class FakeInvoiceCollection:
    """In-memory replacement for MongoDB during unit testing."""

    def __init__(self):
        self.documents = {}
        self.next_id = 1

    def insert_one(self, invoice_data):
        invoice_id = self.next_id
        self.next_id += 1

        invoice_data["_id"] = invoice_id
        self.documents[invoice_id] = invoice_data

        return SimpleNamespace(inserted_id=invoice_id)

    def find_one(self, query):
        invoice_id = query.get("_id")
        return self.documents.get(invoice_id)

    def update_one(self, query, update):
        invoice_id = query.get("_id")
        document = self.documents.get(invoice_id)

        if document is None:
            return SimpleNamespace(matched_count=0, modified_count=0)

        new_status = update["$set"]["extraction.status"]
        document["extraction"]["status"] = new_status
        document["updated_at"] = update["$set"]["updated_at"]

        return SimpleNamespace(matched_count=1, modified_count=1)


def test_invoice_document(monkeypatch):

    # Replace the real MongoDB collection with an in-memory collection.
    fake_collection = FakeInvoiceCollection()

    monkeypatch.setattr(
        document_manager,
        "invoice_collection",
        fake_collection
    )

    # Build invoice document.
    invoice = InvoiceExtractionCreate(

        invoice_number="INV-2026-002",

        vendor=VendorInfo(
            name="ABC Technologies",
            gstin="36ABCDE1234F1Z5",
            sql_vendor_id=12
        ),

        invoice_date=date(2026, 11, 15),

        currency="INR",

        line_items=[

            InvoiceLineItem(
                description="Software License",
                quantity=Decimal("1"),
                unit_price=Decimal("20000"),
                line_total=Decimal("20000")
            ),

            InvoiceLineItem(
                description="Technical Support",
                quantity=Decimal("1"),
                unit_price=Decimal("5000"),
                line_total=Decimal("5000")
            )

        ],

        tax_breakdown=[

            TaxComponent(
                tax_type="CGST",
                rate=Decimal("9"),
                amount=Decimal("2250")
            ),

            TaxComponent(
                tax_type="SGST",
                rate=Decimal("9"),
                amount=Decimal("2250")
            )

        ],

        totals=InvoiceTotals(
            subtotal=Decimal("25000"),
            tax_total=Decimal("4500"),
            grand_total=Decimal("29500")
        ),

        payment_terms=PaymentTerms(
            credit_days=30,
            payment_method="BANK_TRANSFER"
        ),

        extraction=ExtractionInfo(
            status="COMPLETED",
            method="OCR",
            model="invoice-extractor-v1",
            confidence=0.96
        )

    )

    # INSERT
    invoice_id = document_manager.register_invoice_extraction(invoice)

    assert invoice_id is not None

    # READ
    saved_invoice = document_manager.get_invoice_extraction(invoice_id)

    assert saved_invoice is not None
    assert saved_invoice["invoice_number"] == "INV-2026-002"

    # Verify Decimal values were converted to BSON Decimal128.
    assert isinstance(
        saved_invoice["totals"]["grand_total"],
        Decimal128
    )

    assert (
        saved_invoice["totals"]["grand_total"].to_decimal()
        == Decimal("29500")
    )

    # Verify date was converted to a datetime.
    assert isinstance(saved_invoice["invoice_date"], datetime)

    # Verify normalized invoice identity.
    assert saved_invoice["invoice_number_normalized"] == "INV-2026-002"
    assert saved_invoice["vendor"]["identity_key"] == "GSTIN:36ABCDE1234F1Z5"

    # UPDATE
    result = document_manager.update_extraction_status(
        invoice_id,
        "VERIFIED"
    )

    assert result.modified_count == 1

    updated_invoice = document_manager.get_invoice_extraction(invoice_id)

    assert updated_invoice["extraction"]["status"] == "VERIFIED"