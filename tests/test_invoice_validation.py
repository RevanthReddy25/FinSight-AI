from datetime import date
from decimal import Decimal

import pytest

from pydantic import ValidationError

from app.mongodb.document_schemas import (
    InvoiceExtractionCreate
)


def valid_invoice_data():

    return {
        "invoice_number": "INV-2026-003",

        "vendor": {
            "name": "ABC Technologies",
            "gstin": "36ABCDE1234F1Z5",
            "sql_vendor_id": 12
        },

        "invoice_date": date(2026, 11, 15),

        "currency": "INR",

        "line_items": [
            {
                "description": "Software services",
                "quantity": Decimal("1"),
                "unit_price": Decimal("20000"),
                "line_total": Decimal("20000")
            },
            {
                "description": "Consulting services",
                "quantity": Decimal("1"),
                "unit_price": Decimal("5000"),
                "line_total": Decimal("5000")
            }
        ],

        "tax_breakdown": [
            {
                "tax_type": "CGST",
                "rate": Decimal("9"),
                "amount": Decimal("2250")
            },
            {
                "tax_type": "SGST",
                "rate": Decimal("9"),
                "amount": Decimal("2250")
            }
        ],

        "totals": {
            "subtotal": Decimal("25000"),
            "tax_total": Decimal("4500"),
            "grand_total": Decimal("29500")
        },

        "payment_terms": {
            "credit_days": 30,
            "payment_method": "BANK_TRANSFER"
        },

        "extraction": {
            "status": "COMPLETED",
            "method": "OCR",
            "model": "invoice-extractor-v1",
            "confidence": 0.96
        }
    }


def test_valid_invoice():

    invoice = InvoiceExtractionCreate(
        **valid_invoice_data()
    )

    assert invoice.totals.grand_total == Decimal("29500")


def test_invalid_line_total():

    data = valid_invoice_data()

    data["line_items"][0]["line_total"] = Decimal("19000")

    with pytest.raises(ValidationError):

        InvoiceExtractionCreate(**data)


def test_invalid_subtotal():

    data = valid_invoice_data()

    data["totals"]["subtotal"] = Decimal("26000")

    with pytest.raises(ValidationError):

        InvoiceExtractionCreate(**data)


def test_invalid_tax_total():

    data = valid_invoice_data()

    data["totals"]["tax_total"] = Decimal("4000")

    with pytest.raises(ValidationError):

        InvoiceExtractionCreate(**data)


def test_invalid_grand_total():

    data = valid_invoice_data()

    data["totals"]["grand_total"] = Decimal("30000")

    with pytest.raises(ValidationError):

        InvoiceExtractionCreate(**data)