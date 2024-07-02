from models.interfaces import ScoreUpdaterInput as Input, Output
from models.constants import OutputStatus
from bson import ObjectId
from db.users import get_user_collection, get_user_stats_collection


game_type_to__dictionary_key_mapping = {
    "CARD": "cardGameStats",
    "QUIZ": "quizGameStats",
}

class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input


    def _update_game_score(self, user_id, score) -> dict:
        user_collection = get_user_collection()
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        user_stats_id = user.get("userGameStats")
        user_stats_collection = get_user_stats_collection()

        if not user_stats_id:

            game_stats = {
                str(self.input.level) : {
                    "score" : score
                }
            }

            result = user_stats_collection.insert_one({game_type_to__dictionary_key_mapping.get(self.input.game_type): game_stats})
            inserted_id = result.inserted_id

            user_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"userGameStats": inserted_id}},
            )

        else:
            user_stats = user_stats_collection.find_one({"_id": ObjectId(user_stats_id)})
            game_stats = user_stats.get(game_type_to__dictionary_key_mapping.get(self.input.game_type))

            if not game_stats:
                game_stats = {
                    str(self.input.level) : {
                        "score" : score
                    }
                }
                user_stats_collection.insert_one({game_type_to__dictionary_key_mapping.get(self.input.game_type): game_stats})

            else:
                level_stats = game_stats.get(str(self.input.level))
                if not level_stats:
                    game_stats[str(self.input.level)] = {
                        "score" : score
                    }

                else:
                    level_stats["score"] = score

                user_stats_collection.update_one(
                    {"_id": ObjectId(user_stats_id)},
                    {"$set": {game_type_to__dictionary_key_mapping.get(self.input.game_type): game_stats}},
                )


    def compute(self):
        
        self._update_game_score(self.input.user_id, self.input.user_score)
        self._update_game_score(self.input.saarthi_id, self.input.saarthi_score)

        return Output(
            output_details="",
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched game config"
        )