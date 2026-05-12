import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client.get_database("attendance_app")

def get_collection(name:str):
    return db.get_collection(name)
def get_health():
    try:
        client.admin.command('ismaster')
        return True
    except ConnectionFailure:
        print("connection failure")
        return False
