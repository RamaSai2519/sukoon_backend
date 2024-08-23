from db.base import Database
from pymongo.collection import Collection

def get_experts_collections() -> Collection:
    client = Database().client

    db = client["test"]
    quiz_questions_collection = db["experts"]
    return quiz_questions_collection

def get_categories_collection() -> Collection:
    client = Database().client

    db = client["test"]
    categories_collection = db["categories"]
    return categories_collection

def get_expertlogs_collection() -> Collection:
    client = Database().client

    db = client["test"]
    expertlogs_collection = db["expertlogs"]
    return expertlogs_collection

def get_timings_collection() -> Collection:
    client = Database().client

    db = client["test"]
    timings_collection = db["timings"]
    return timings_collection