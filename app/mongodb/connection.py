import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

MONGODB_DATABASE = os.getenv(
    "MONGODB_DATABASE",
    "finsightai"
)

if not MONGODB_URI:
    raise ValueError(
        "MONGODB_URI is missing. Check your .env file."
    )


client = MongoClient(
    MONGODB_URI,
    server_api=ServerApi(
        version="1",
        strict=True,
        deprecation_errors=True
    ),
    serverSelectionTimeoutMS=5000
)

mongodb = client[MONGODB_DATABASE]


def check_mongodb_connection():

    try:
        client.admin.command("ping")

        print("MongoDB Atlas connected successfully!")

        return True

    except Exception as error:

        print("MongoDB connection failed:", error)

        return False


def close_mongodb_connection():

    client.close()

    print("MongoDB connection closed.")