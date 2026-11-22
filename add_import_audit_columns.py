import sqlite3

connection = sqlite3.connect("finsight.db")
cursor = connection.cursor()

migrations = {
    "import_batches": [
        ("uploaded_by", "VARCHAR(150)"),
        ("rejected_records", "INTEGER NOT NULL DEFAULT 0"),
        ("unresolved_vendor_count", "INTEGER NOT NULL DEFAULT 0"),
        ("error_message", "VARCHAR(2000)"),
        ("completed_at", "DATETIME")
    ],
    "financial_transactions": [
        ("import_batch_id", "INTEGER")
    ]
}

try:

    for table, columns_to_add in migrations.items():

        cursor.execute(f"PRAGMA table_info({table})")

        existing_columns = {
            column[1]
            for column in cursor.fetchall()
        }

        for column_name, column_type in columns_to_add:

            if column_name not in existing_columns:

                cursor.execute(
                    f"ALTER TABLE {table} "
                    f"ADD COLUMN {column_name} {column_type}"
                )

                print(
                    f"Added {column_name} to {table}"
                )

            else:

                print(
                    f"{column_name} already exists in {table}"
                )

    connection.commit()

    print("\nMigration completed.")

except Exception:

    connection.rollback()
    raise

finally:

    connection.close()