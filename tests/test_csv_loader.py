import pandas as pd
import pytest

from app.ingestion.csv_loader import load_financial_csv


def test_load_valid_csv(tmp_path):

    csv_file = tmp_path / "transactions.csv"

    csv_file.write_text(
        "project_id,vendor_id,category_id,description,"
        "amount,transaction_date,transaction_type,status\n"
        "1,1,1,Microsoft Subscription,25000.00,"
        "2026-11-01,EXPENSE,PENDING\n",
        encoding="utf-8"
    )

    df = load_financial_csv(str(csv_file))

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.iloc[0]["description"] == "Microsoft Subscription"
    assert df.iloc[0]["amount"] == "25000.00"
    assert df.iloc[0]["source_row"] == 2


def test_missing_csv_file():

    with pytest.raises(FileNotFoundError):
        load_financial_csv("missing.csv")


def test_missing_columns(tmp_path):

    csv_file = tmp_path / "invalid.csv"

    csv_file.write_text(
        "project_id,vendor_id,amount\n"
        "1,1,25000\n",
        encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Missing required columns"):
        load_financial_csv(str(csv_file))


def test_invalid_file_extension(tmp_path):

    file = tmp_path / "transactions.txt"
    file.write_text("test", encoding="utf-8")

    with pytest.raises(ValueError, match="Only CSV files"):
        load_financial_csv(str(file))