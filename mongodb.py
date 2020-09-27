from dotenv import main
import pymongo
import os
import dotenv
dotenv.load_dotenv()

DATABASE_SECRET = os.getenv('DATABASE_SECRET')


def get_database(collection_name):
    client = pymongo.MongoClient(DATABASE_SECRET)
    db = client.dredy_bot
    collection = db[collection_name]
    return client, db, collection
