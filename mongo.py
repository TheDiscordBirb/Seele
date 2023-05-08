import os

from pymongo import MongoClient


def get_database():
    connection_string = os.environ["CONNECTION_STRING"]
    client = MongoClient(connection_string)
    return client["Seele"]
