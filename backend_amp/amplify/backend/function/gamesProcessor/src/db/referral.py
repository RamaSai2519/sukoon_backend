from db.base import Database


def get_user_referral_collection():
    client = Database().client

    db = client["test"]
    user_referral_collection = db["userreferrals"]
    return user_referral_collection