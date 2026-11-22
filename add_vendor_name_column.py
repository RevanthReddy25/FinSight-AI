import sqlite3

# Connect to your existing database
connection = sqlite3.connect("finsight.db")

cursor = connection.cursor()

# Check whether the column already exists
cursor.execute("PRAGMA table_info(financial_transactions)")

columns = [column[1] for column in cursor.fetchall()]

if "vendor_name_raw" not in columns:

    cursor.execute("""
        ALTER TABLE financial_transactions
        ADD COLUMN vendor_name_raw VARCHAR(255)
    """)

    connection.commit()

    print("vendor_name_raw column added successfully.")

else:
    print("vendor_name_raw column already exists.")

connection.close()