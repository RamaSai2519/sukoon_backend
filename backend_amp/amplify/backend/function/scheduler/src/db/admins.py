from db.base import Database
from pymongo.collection import Collection


def get_fcm_token_collection() -> Collection:
    client = Database().client

    db = client["test"]
    fcm_token_collection = db["fcm_tokens"]
    return fcm_token_collection


def get_error_logs_collection() -> Collection:
    client = Database().client

    db = client["test"]
    error_log_collection = db["errorlogs"]
    return error_log_collection
