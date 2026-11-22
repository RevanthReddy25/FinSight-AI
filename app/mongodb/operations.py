from app.mongodb.collections import invoice_collection


def create_invoice(invoice):

    result = invoice_collection.insert_one(invoice)

    return result.inserted_id


def get_invoice(invoice_id):

    return invoice_collection.find_one(
        {"_id": invoice_id}
    )


def get_all_invoices():

    return list(invoice_collection.find())


def update_invoice(invoice_id, update_data):

    return invoice_collection.update_one(
        {"_id": invoice_id},
        {"$set": update_data}
    )


def delete_invoice(invoice_id):

    return invoice_collection.delete_one(
        {"_id": invoice_id}
    )


def get_invoices_by_vendor(vendor_name):

    return list(
        invoice_collection.find(
            {"vendor.name": vendor_name}
        )
    )