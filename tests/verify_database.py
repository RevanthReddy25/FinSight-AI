import sqlite3

connection = sqlite3.connect("finsight.db")

cursor = connection.cursor()

# Check transaction table columns
cursor.execute("PRAGMA table_info(financial_transactions)")

print("\nFinancial Transactions Columns:")

for column in cursor.fetchall():
    print(column[1])

# Check existing tables
cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
""")

print("\nDatabase Tables:")

for table in cursor.fetchall():
    print(table[0])

connection.close()