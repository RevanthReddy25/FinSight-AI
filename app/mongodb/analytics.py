from app.mongodb.collections import invoice_collection

from app.mongodb.connection import mongodb

invoice_collection = mongodb["invoice_extractions"]


def vendor_wise_expenses():

    pipeline = [

        # Only verified invoices
        {
            "$match": {
                "extraction_status": "VERIFIED"
            }
        },

        # Group invoices by vendor
        {
            "$group": {
                "_id": "$vendor.name",

                "total_expenses": {
                    "$sum": "$amount"
                },

                "invoice_count": {
                    "$sum": 1
                },

                "average_invoice": {
                    "$avg": "$amount"
                }
            }
        },

        # Highest spending vendor first
        {
            "$sort": {
                "total_expenses": -1
            }
        }
    ]

    results = invoice_collection.aggregate(pipeline)

    print("\nVENDOR-WISE EXPENSE REPORT")

    for result in results:

        print("\nVendor:", result["_id"])
        print("Total Expenses:", result["total_expenses"])
        print("Invoice Count:", result["invoice_count"])
        print("Average Invoice:", result["average_invoice"])


def category_wise_expenses():

    pipeline = [

        {
            "$match": {
                "extraction_status": "VERIFIED"
            }
        },

        {
            "$group": {

                "_id": "$category",

                "total_expenses": {
                    "$sum": "$amount"
                },

                "invoice_count": {
                    "$sum": 1
                }
            }
        },

        {
            "$sort": {
                "total_expenses": -1
            }
        }
    ]

    results = invoice_collection.aggregate(pipeline)

    print("\nCATEGORY-WISE EXPENSE REPORT")

    for result in results:

        print("\nCategory:", result["_id"])
        print("Total Expenses:", result["total_expenses"])
        print("Invoice Count:", result["invoice_count"])