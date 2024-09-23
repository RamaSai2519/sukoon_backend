from db.base import Database
from pymongo.collection import Collection


def get_calls_collection() -> Collection:
    client = Database().client

    db = client["test"]
    calls_collection = db["calls"]
    return calls_collection

def get_callsmeta_collection() -> Collection:
    client = Database().client

    db = client["test"]
    callsmeta_collection = db["callsmeta"]
    return callsmeta_collection

def get_schedules_collection() -> Collection:
    client = Database().client

    db = client["test"]
    schedules_collection = db["schedules"]
    return schedules_collection
