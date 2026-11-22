from app.database import SessionLocal
from app.models import Vendor, UnresolvedVendor
from app.vendor_resolution import reconcile_unresolved_vendors

db = SessionLocal()

try:
    # Step 1: Check whether vendor already exists
    vendor = db.query(Vendor).filter(
        Vendor.vendor_name == "ABC Technologies"
    ).first()

    # Step 2: Add vendor if it doesn't exist
    if not vendor:
        vendor = Vendor(
            vendor_name="ABC Technologies"
        )
        db.add(vendor)
        db.commit()
        db.refresh(vendor)

    print("Vendor ID:", vendor.vendor_id)

    # Step 3: Run reconciliation
    result = reconcile_unresolved_vendors(db)

    print("\nReconciliation result:")
    print(result)

    # Step 4: Check updated unresolved vendor
    unresolved = db.query(UnresolvedVendor).filter(
        UnresolvedVendor.normalized_vendor_name == "abc technologies"
    ).first()

    print("\nUpdated vendor record:")
    print("Vendor name:", unresolved.vendor_name_raw)
    print("Status:", unresolved.status)
    print("Resolved vendor ID:", unresolved.resolved_vendor_id)

finally:
    db.close()