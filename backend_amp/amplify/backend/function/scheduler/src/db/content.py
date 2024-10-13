from db.base import Database
from pymongo.collection import Collection


def get_content_posts_collection() -> Collection:
    client = Database().client

    db = client["test"]
    content_posts_collection = db["content_posts"]
    return content_posts_collection
