from db.base import Database
from pymongo.collection import Collection


def get_whatsapp_templates_collection() -> Collection:
    client = Database().client

    db = client["whatsapp"]
    templates_collection = db["templates"]
    return templates_collection


def get_whatsapp_temp_collection() -> Collection:
    client = Database().client

    db = client["whatsapp"]
    temp_collection = db["temp"]
    return temp_collection
