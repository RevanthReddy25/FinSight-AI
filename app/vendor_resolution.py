from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import (
    Vendor,
    FinancialTransaction,
    UnresolvedVendor
)

from datetime import datetime
import re


# --------------------------------------------------
# 1. NORMALIZE VENDOR NAME
# --------------------------------------------------

def normalize_vendor_name(vendor_name: str) -> str:
    """
    Standardize vendor names for matching.

    Examples:
        " Microsoft " -> "microsoft"
        "MICROSOFT"   -> "microsoft"
        "Amazon  Web Services" -> "amazon web services"
    """

    if not vendor_name:
        return ""

    normalized = vendor_name.strip().lower()

    # Replace multiple spaces with a single space
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized


# --------------------------------------------------
# 2. FIND VENDOR IN VENDOR MASTER
# --------------------------------------------------

def find_vendor_by_name(
    db: Session,
    vendor_name: str
):
    """
    Find an existing vendor using normalized name matching.

    Returns:
        Vendor object if exactly one match exists.
        None if no match or multiple matches exist.
    """

    normalized_name = normalize_vendor_name(vendor_name)

    if not normalized_name:
        return None

    vendors = db.scalars(
        select(Vendor)
    ).all()

    matches = [
        vendor
        for vendor in vendors
        if normalize_vendor_name(vendor.vendor_name)
        == normalized_name
    ]

    # Avoid automatically assigning an ambiguous match
    if len(matches) == 1:
        return matches[0]

    return None

# --------------------------------------------------
# FIND VENDOR USING GSTIN
# --------------------------------------------------

def find_vendor_by_gstin(
    db: Session,
    gstin: str
):
    """
    Find a vendor using an exact normalized GSTIN.

    Returns:
        Vendor object if exactly one match exists.
        None otherwise.
    """

    if not gstin:
        return None

    normalized_gstin = gstin.strip().upper()

    return db.scalar(
        select(Vendor).where(
            Vendor.gstin == normalized_gstin
        )
    )
# --------------------------------------------------
# 3. ADD OR UPDATE UNRESOLVED VENDOR
# --------------------------------------------------

def add_unresolved_vendor(
    db: Session,
    vendor_name: str,
    gstin: str | None = None
):
    """
    Add or update an unresolved vendor.

    GSTIN is preserved when available.

    If the same normalized name appears with a
    different GSTIN, flag the existing record
    for manual review rather than merging identities.
    """

    normalized_name = normalize_vendor_name(vendor_name)

    if not normalized_name:
        return None

    normalized_gstin = (
        gstin.strip().upper()
        if gstin
        else None
    )

    unresolved_vendor = db.scalar(
        select(UnresolvedVendor).where(
            UnresolvedVendor.normalized_vendor_name
            == normalized_name
        )
    )

    if unresolved_vendor:

        # Existing GSTIN conflicts with newly extracted GSTIN
        if (
            unresolved_vendor.gstin
            and normalized_gstin
            and unresolved_vendor.gstin != normalized_gstin
        ):

            unresolved_vendor.status = "REVIEW"

            unresolved_vendor.occurrence_count += 1

            unresolved_vendor.last_seen_at = datetime.utcnow()

            return unresolved_vendor

        # Preserve GSTIN if it was previously unavailable
        if normalized_gstin and not unresolved_vendor.gstin:

            unresolved_vendor.gstin = normalized_gstin

        unresolved_vendor.occurrence_count += 1

        unresolved_vendor.last_seen_at = datetime.utcnow()

        return unresolved_vendor

    unresolved_vendor = UnresolvedVendor(
        vendor_name_raw=vendor_name.strip(),
        normalized_vendor_name=normalized_name,
        gstin=normalized_gstin,
        occurrence_count=1,
        status="PENDING"
    )

    db.add(unresolved_vendor)

    db.flush()

    return unresolved_vendor

# --------------------------------------------------
# 4. RESOLVE VENDOR
# --------------------------------------------------

def resolve_vendor(
    db: Session,
    vendor_id: int | None = None,
    vendor_name: str | None = None,
    gstin: str | None = None
):
    """
    Resolve vendor using the following priority:

    1. Validate supplied vendor ID.
    2. Match exact GSTIN.
    3. If GSTIN is supplied but unmatched, send for review.
    4. If GSTIN is absent, use normalized vendor name.
    5. Otherwise, add to unresolved queue.
    """

    # Priority 1: Vendor ID

    if vendor_id is not None:

        vendor = db.get(Vendor, vendor_id)

        if not vendor:
            raise ValueError(
                f"Vendor ID {vendor_id} does not exist."
            )

        return vendor.vendor_id

    # Priority 2: GSTIN

    if gstin:

        normalized_gstin = gstin.strip().upper()

        vendor = find_vendor_by_gstin(
            db,
            normalized_gstin
        )

        if vendor:
            return vendor.vendor_id

        if vendor_name:

            add_unresolved_vendor(
                db,
                vendor_name,
                normalized_gstin
            )

        return None

    # Priority 3: Vendor name

    if not vendor_name or not vendor_name.strip():
        return None

    vendor = find_vendor_by_name(
        db,
        vendor_name
    )

    if vendor:
        return vendor.vendor_id

    # Priority 4: Unresolved

    add_unresolved_vendor(
        db,
        vendor_name
    )

    return None

# --------------------------------------------------
# 5. RECONCILE UNRESOLVED VENDORS
# --------------------------------------------------

def reconcile_unresolved_vendors(db: Session):
    """
    Reconcile pending unresolved vendors.

    GSTIN-based matching takes priority.
    Name matching is used only when GSTIN is unavailable.
    """

    pending_vendors = db.scalars(
        select(UnresolvedVendor).where(
            UnresolvedVendor.status == "PENDING"
        )
    ).all()

    resolved_count = 0
    updated_transactions = 0

    unmatched_transactions = db.scalars(
        select(FinancialTransaction).where(
            FinancialTransaction.vendor_id.is_(None),
            FinancialTransaction.vendor_name_raw.is_not(None)
        )
    ).all()

    for unresolved in pending_vendors:

        # GSTIN matching takes priority

        if unresolved.gstin:

            vendor = find_vendor_by_gstin(
                db,
                unresolved.gstin
            )

        else:

            vendor = find_vendor_by_name(
                db,
                unresolved.vendor_name_raw
            )

        if not vendor:
            continue

        matching_transactions = [
            transaction
            for transaction in unmatched_transactions
            if normalize_vendor_name(
                transaction.vendor_name_raw
            ) == unresolved.normalized_vendor_name
        ]

        for transaction in matching_transactions:

            transaction.vendor_id = vendor.vendor_id

            updated_transactions += 1

        unresolved.status = "RESOLVED"

        unresolved.resolved_vendor_id = vendor.vendor_id

        resolved_count += 1

    db.flush()

    return {
        "resolved_vendors": resolved_count,
        "updated_transactions": updated_transactions
    }