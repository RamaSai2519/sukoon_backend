from db.base import Database
from pymongo.collection import Collection

def get_whatsapp_templates() -> Collection:
    client = Database().client

    db = client["whatsapp"]
    templates_collection = db["templates"]
    return templates_collection