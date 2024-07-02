from db.base import Database


def get_otp_collection():
    client = Database().client

    db = client["test"]
    otp_collection = db["otp"]
    return otp_collection