from app.mongodb.indexes import (
    create_invoice_indexes,
    list_invoice_indexes
)

if __name__ == "__main__":

    create_invoice_indexes()

    list_invoice_indexes()