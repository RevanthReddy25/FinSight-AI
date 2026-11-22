from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "project_id",
    "vendor_id",
    "category_id",
    "description",
    "amount",
    "transaction_date",
    "transaction_type",
    "status"
]


def load_financial_csv(file_path: str) -> pd.DataFrame:

    path = Path(file_path)

    # Check whether file exists
    if not path.exists():
        raise FileNotFoundError(
            f"CSV file not found: {file_path}"
        )

    # Check file extension
    if path.suffix.lower() != ".csv":
        raise ValueError(
            "Only CSV files are supported"
        )

    # Read CSV
    df = pd.read_csv(
        path,
        dtype="string",
        keep_default_na=False,
        encoding="utf-8-sig"
    )

    # Check required columns
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    # Vendor name is optional for backward compatibility
    if "vendor_name" not in df.columns:
        df["vendor_name"] = ""

    # Ensure blank values are represented consistently
    df["vendor_name"] = df["vendor_name"].fillna("").astype(str).str.strip()
    df["vendor_id"] = df["vendor_id"].fillna("").astype(str).str.strip()

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Preserve original CSV row number for error reporting
    df.insert(
        0,
        "source_row",
        range(2, len(df) + 2)
    )

    return df