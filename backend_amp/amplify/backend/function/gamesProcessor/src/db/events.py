from db.base import Database
from pymongo.collection import Collection


def get_events_collection() -> Collection:
    client = Database().client

    db = client["events"]
    events_collection = db["events"]
    return events_collection


def get_event_users_collection() -> Collection:
    client = Database().client

    db = client["events"]
    eventusers_collection = db["event_users"]
    return eventusers_collection


def get_contribute_events_collection() -> Collection:
    client = Database().client

    db = client["events"]
    contribute_events_collection = db["contribute_events"]
    return contribute_events_collection


def get_become_saarthis_collection() -> Collection:
    client = Database().client

    db = client["test"]
    become_saarthis_collection = db["becomesaarthis"]
    return become_saarthis_collection
