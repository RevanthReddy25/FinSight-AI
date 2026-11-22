from app.mongodb import check_mongodb_connection

if __name__ == "__main__":

    connection_status = check_mongodb_connection()

    if connection_status:
        print("FinSightAI MongoDB setup completed.")

    else:
        print("Please check your Atlas configuration.")