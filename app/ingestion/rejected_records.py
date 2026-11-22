import json

import pandas as pd

from app.models import RejectedTransaction


def make_json_safe(value):
    """
    Convert Pandas and Python values into JSON-compatible values.
    """

    if value is None or pd.isna(value):
        return None

    if hasattr(value, "item"):
        value = value.item()

    return str(value) if not isinstance(
        value,
        (str, int, float, bool, list, dict)
    ) else value


def save_rejected_records(
    db,
    rejected_df,
    batch_id,
    rejection_stage="VALIDATION"
):
    """
    Save rejected CSV rows with original data and validation errors.
    """

    if rejected_df.empty:
        return 0

    saved_count = 0

    for _, row in rejected_df.iterrows():

        raw_data = {
            key: make_json_safe(value)
            for key, value in row.drop(
                labels=["errors"],
                errors="ignore"
            ).to_dict().items()
        }

        errors = row.get("errors", [])

        if isinstance(errors, str):
            errors = [errors]

        elif not isinstance(errors, list):
            errors = list(errors)

        rejected_record = RejectedTransaction(
            import_batch_id=batch_id,
            source_row=int(row["source_row"]),
            raw_data=raw_data,
            errors=errors,
            rejection_stage=rejection_stage
        )

        db.add(rejected_record)
        saved_count += 1

    # Flush after all records have been added.
    db.flush()

    # Verify the final number of saved records.
    if saved_count != len(rejected_df):
        raise RuntimeError(
            f"Rejected record count mismatch: "
            f"expected {len(rejected_df)}, saved {saved_count}"
        )

    return saved_count