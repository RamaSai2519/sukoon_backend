from db.base import Database


def get_calls_collection():
    client = Database().client

    db = client["test"]
    calls_collection = db["calls"]
    return calls_collection