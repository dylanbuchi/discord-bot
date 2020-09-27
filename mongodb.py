from dotenv import main
import pymongo
import pymongo.errors
import os
import dotenv
from pymongo.errors import AutoReconnect, BulkWriteError
dotenv.load_dotenv()

DATABASE_SECRET = os.getenv('DATABASE_SECRET')


def get_database(collection_name):
    try:
        client = pymongo.MongoClient(DATABASE_SECRET, port=27017)
        db = client.dredy_bot
        collection = db[collection_name]
    except [AutoReconnect, BulkWriteError] as error:
        print("Error", error)
    return client, db, collection
