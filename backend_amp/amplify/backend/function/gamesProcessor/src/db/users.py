from db.base import Database


def get_user_collection():
    client = Database().client

    db = client["test"]
    users_collection = db["users"]
    return users_collection


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


def get_user_notification_collection():
    client = Database().client

    db = client["test"]
    users_game_play_collection = db["usernotifications"]
    return users_game_play_collection

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




