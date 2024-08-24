from db.base import Database


def get_experts_collections():
    client = Database().client

    db = client["test"]
    experts_collection = db["experts"]
    return experts_collection
