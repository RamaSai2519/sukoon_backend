from db.base import Database
from pymongo.collection import Collection

def get_user_referral_collection() -> Collection:
    client = Database().client

    db = client["test"]
    user_referral_collection = db["userreferrals"]
    return user_referral_collection