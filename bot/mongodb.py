import pymongo
import pymongo.errors
import os
import dotenv
import bson.json_util
from pymongo.errors import AutoReconnect, BulkWriteError
dotenv.load_dotenv()

DATABASE_SECRET = os.getenv('DATABASE_SECRET')


def get_database_data(collection, filter: dict):
    """
    get mongodb database data from a collection name by filter
    and return it as a JSON str
    """
    cursor = collection.find_one(filter)
    data = bson.json_util.dumps(cursor)
    return cursor, data


def get_database(collection_name):
    try:
        client = pymongo.MongoClient(DATABASE_SECRET, port=27017)
        db = client.dredy_bot
        collection = db[collection_name]
    except [AutoReconnect, BulkWriteError] as error:
        print("Error", error)
    return client, db, collection
