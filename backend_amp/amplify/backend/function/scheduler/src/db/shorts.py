from db.base import Database


def get_shorts_collections():
    client = Database().client

    db = client["test"]
    quiz_questions_collection = db["shorts"]
    return quiz_questions_collection


def get_shorts_categories_collections():
    client = Database().client

    db = client["test"]
    quiz_questions_collection = db["shortscategories"]
    return quiz_questions_collection


