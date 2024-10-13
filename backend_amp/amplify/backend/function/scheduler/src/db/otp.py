from db.base import Database
from pymongo.collection import Collection


def get_otp_collection() -> Collection:
    client = Database().client

    db = client["test"]
    otp_collection = db["otp"]
    return otp_collection
