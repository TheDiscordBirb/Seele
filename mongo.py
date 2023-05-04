import os

from pymongo import MongoClient
cluster = MongoClient(os.getenv('MONGO_URI'))

db = cluster["Seele"]

# To create a database:
# collection_name = db[collection_name]
tickets = db['tickets']
vanity_roles = db['vanity_roles']
