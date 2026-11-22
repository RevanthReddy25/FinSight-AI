from app.mongodb.operations import (
    create_invoice,
    get_invoice,
    update_invoice
)


def main():

    # Sample invoice document
    invoice = {
        "invoice_number": "CRUD-TEST-001",
        "vendor": {
            "name": "Test Technologies"
        },
        "currency": "INR",
        "description": "Software Services",
        "amount": 10000,
        "status": "PENDING"
    }

    # CREATE
    invoice_id = create_invoice(invoice)

    print("\nInvoice created successfully!")
    print("Invoice ID:", invoice_id)

    # READ
    created_invoice = get_invoice(invoice_id)

    print("\nRetrieved Invoice:")
    print(created_invoice)

    # UPDATE
    update_invoice(
        invoice_id,
        {
            "status": "APPROVED"
        }
    )

    print("\nInvoice updated successfully!")

    # READ UPDATED DOCUMENT
    updated_invoice = get_invoice(invoice_id)

    print("\nUpdated Invoice:")
    print(updated_invoice)

    print("\nMongoDB CRUD operations completed!")


if __name__ == "__main__":
    main()