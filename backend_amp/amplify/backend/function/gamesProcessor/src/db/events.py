from db.base import Database
from pymongo.collection import Collection

def get_events_collection() -> Collection:
    client = Database().client

    db = client["test"]
    events_collection = db["eventconfigs"]
    return events_collection