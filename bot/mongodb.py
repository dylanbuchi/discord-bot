from bot.github_api import update_file_in_github_repo
import json
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
    return cursor


def load_original_data_to(collection, file_name):
    # load original file data to the database
    data = (json.load(open(r'data\original.json', encoding='utf-8')))
    file_data = json.load(open(os.path.join(os.getcwd(), 'data', file_name)))

    filter_id = {'_id': file_data['_id']}
    collection.update_one(filter_id, {'$set': data})

    #UPDATE github file data
    updated_data = get_database_data(collection, filter_id)
    update_file_in_github_repo('data/' + file_name, updated_data)


def get_database(collection_name):
    client = pymongo.MongoClient(DATABASE_SECRET, port=27017)
    db = client.dredy_bot
    collection = db[collection_name]
    return client, collection
