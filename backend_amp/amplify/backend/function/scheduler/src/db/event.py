from db.base import Database


def get_event_configs_collection():
    client = Database().client

    db = client["test"]
    event_configs_collection = db["eventconfigs"]
    return event_configs_collection