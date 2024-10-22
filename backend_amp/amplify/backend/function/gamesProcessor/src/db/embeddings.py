from db.base import Database
from pymongo.collection import Collection


def get_recommendations_collection() -> Collection:
    client = Database().client

    db = client["embeddings"]
    recommendations_collection = db["recommendations"]
    return recommendations_collection
