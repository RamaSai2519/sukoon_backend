from models.interfaces import CalculateWinnerInput as Input, Output
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


    def _calculate_final__game_score(self, user_id) -> dict:
        user_collection = get_user_collection()
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        user_stats_id = user.get("userGameStats")
        user_stats_collection = get_user_stats_collection()

        if not user_stats_id:

            return "user game stats not found", OutputStatus.FAILURE

        else:
            user_stats = user_stats_collection.find_one({"_id": ObjectId(user_stats_id)})
            game_stats = user_stats.get(game_type_to__dictionary_key_mapping.get(self.input.game_type))
            score = 0

            for key, value in game_stats.items():
                score += value.get("score", 0)
            return score


    def compute(self):
        
        user_score = self._calculate_final__game_score(self.input.user_id)
        saarthi_score = self._calculate_final__game_score(self.input.saarthi_id)

        return Output(
            output_details= {"user_score": user_score, "saarthi_score": saarthi_score},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched game winner"
        )