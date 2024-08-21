from db.base import Database


def get_event_configs_collection():
    client = Database().client

    db = client["test"]
    event_configs_collection = db["event_configs"]
    return event_configs_collection