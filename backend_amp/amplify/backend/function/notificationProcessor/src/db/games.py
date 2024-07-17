from db.base import Database

def get_games_config_collection():
    client = Database().client

    db = client["games"]
    games_config_collection = db["games_config"]
    return games_config_collection


def get_quiz_questions_collections():
    client = Database().client

    db = client["test"]
    quiz_questions_collection = db["quizquestions"]
    return quiz_questions_collection






