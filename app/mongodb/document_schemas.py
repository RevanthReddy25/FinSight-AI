from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    model_validator
)


# Allow a maximum difference of one paisa
TOLERANCE = Decimal("0.01")


class VendorInfo(BaseModel):

    name: str = Field(min_length=1)

    gstin: str | None = Field(
        default=None,
        pattern=r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$"
    )

    sql_vendor_id: int | None = Field(
        default=None,
        ge=1
    )


class InvoiceLineItem(BaseModel):

    description: str = Field(min_length=1)

    quantity: Decimal = Field(gt=0)

    unit_price: Decimal = Field(ge=0)

    line_total: Decimal = Field(ge=0)

    @model_validator(mode="after")
    def validate_line_total(self):

        expected_total = self.quantity * self.unit_price

        if abs(self.line_total - expected_total) > TOLERANCE:

            raise ValueError(
                f"Line total mismatch. "
                f"Expected {expected_total}, "
                f"received {self.line_total}"
            )

        return self


class TaxComponent(BaseModel):

    tax_type: str

    rate: Decimal = Field(ge=0, le=100)

    amount: Decimal = Field(ge=0)


class InvoiceTotals(BaseModel):

    subtotal: Decimal = Field(ge=0)

    tax_total: Decimal = Field(ge=0)

    grand_total: Decimal = Field(ge=0)


class PaymentTerms(BaseModel):

    credit_days: int = Field(ge=0)

    payment_method: str


class ExtractionInfo(BaseModel):

    status: Literal[
        "PENDING",
        "COMPLETED",
        "VERIFIED",
        "FAILED"
    ]

    method: str

    model: str | None = None

    confidence: float = Field(
        ge=0,
        le=1
    )


class InvoiceExtractionCreate(BaseModel):

    invoice_number: str = Field(min_length=1)

    vendor: VendorInfo

    invoice_date: date

    currency: str = Field(
        pattern=r"^[A-Z]{3}$"
    )

    line_items: list[InvoiceLineItem] = Field(
        min_length=1
    )

    tax_breakdown: list[TaxComponent] = Field(
        default_factory=list
    )

    totals: InvoiceTotals

    payment_terms: PaymentTerms

    extraction: ExtractionInfo

    @model_validator(mode="after")
    def validate_invoice_totals(self):

        # 1. Validate subtotal

        calculated_subtotal = sum(
            (item.line_total for item in self.line_items),
            Decimal("0")
        )

        if abs(
            self.totals.subtotal - calculated_subtotal
        ) > TOLERANCE:

            raise ValueError(
                f"Subtotal mismatch. "
                f"Expected {calculated_subtotal}, "
                f"received {self.totals.subtotal}"
            )

        # 2. Validate tax total when a breakdown is provided

        if self.tax_breakdown:

            calculated_tax = sum(
                (tax.amount for tax in self.tax_breakdown),
                Decimal("0")
            )

            if abs(
                self.totals.tax_total - calculated_tax
            ) > TOLERANCE:

                raise ValueError(
                    f"Tax total mismatch. "
                    f"Expected {calculated_tax}, "
                    f"received {self.totals.tax_total}"
                )

        # 3. Validate grand total

        calculated_grand_total = (
            self.totals.subtotal +
            self.totals.tax_total
        )

        if abs(
            self.totals.grand_total -
            calculated_grand_total
        ) > TOLERANCE:

            raise ValueError(
                f"Grand total mismatch. "
                f"Expected {calculated_grand_total}, "
                f"received {self.totals.grand_total}"
            )

        return self