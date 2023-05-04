import os

from pymongo import MongoClient


def get_database():
    client = MongoClient(os.getenv('CONNECTION_STRING'))
    return client['Seele']
