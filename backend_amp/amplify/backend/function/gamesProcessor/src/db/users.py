from db.base import Database, PrDatabase
from pymongo.collection import Collection


def get_user_collection() -> Collection:
    client = Database().client

    db = client["test"]
    users_collection = db["users"]
    return users_collection


def get_meta_collection() -> Collection:
    client = Database().client

    db = client["test"]
    meta_collection = db["meta"]
    return meta_collection


def get_admins_collection() -> Collection:
    client = Database().client

    db = client["test"]
    admins_collection = db["admins"]
    return admins_collection


def get_user_stats_collection():
    client = Database().client

    db = client["test"]
    users_collection = db["usergamestats"]
    return users_collection


def get_user_game_plays_collection():
    client = Database().client

    db = client["test"]
    users_game_play_collection = db["usergameplays"]
    return users_game_play_collection


def get_user_notification_collection() -> Collection:
    client = Database().client

    db = client["test"]
    users_game_play_collection = db["usernotifications"]
    return users_game_play_collection


def get_prusers_collection() -> Collection:
    client = PrDatabase().client

    db = client["prerana"]
    prusers_collection = db["users"]
    return prusers_collection


def get_user_webhook_messages_collection():
    client = Database().client

    db = client["test"]
    users_game_play_collection = db["userwebhookmessages"]
    return users_game_play_collection


def get_user_whatsapp_feedback_collection():
    client = Database().client

    db = client["test"]
    users_whatsapp_feedback_collection = db["userwhatsappfeedback"]
    return users_whatsapp_feedback_collection


def get_user_fcm_token_collection():
    client = Database().client

    db = client["test"]
    user_fcm_token_collection = db["userfcmtokens"]
    return user_fcm_token_collection


def get_user_payment_collection():
    client = Database().client

    db = client["test"]
    user_payment_collection = db["userpayments"]
    return user_payment_collection


def get_club_interests_collection() -> Collection:
    client = Database().client

    db = client["test"]
    club_interests_collection = db["club_intersts"]
    return club_interests_collection
