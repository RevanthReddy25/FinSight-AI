from app.mongodb.connection import check_mongodb_connection

from app.mongodb.indexes import (
    create_duplicate_protection_index
)


if __name__ == "__main__":

    if check_mongodb_connection():

        create_duplicate_protection_index()

    else:

        print("MongoDB connection failed.")