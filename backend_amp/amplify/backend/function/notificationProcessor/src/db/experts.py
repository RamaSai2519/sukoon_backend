from db.base import Database


def get_experts_collections():
    client = Database().client

    db = client["test"]
    quiz_questions_collection = db["experts"]
    return quiz_questions_collection
