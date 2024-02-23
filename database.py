from pymongo import MongoClient
import os

mongo_client = MongoClient(os.environ.get("MONGODB_URI"))
db = mongo_client.bananabread
roles_collection = db.roles
