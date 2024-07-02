from models.interfaces import UpdateGamePlayInput as Input, Output
from models.constants import OutputStatus
from db.users import get_user_game_plays_collection

class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input


    def _update_game_play(self, user_id, opponent_id, user_score, opponent_score, reward_amount) -> dict:

        user_game_play_collection = get_user_game_plays_collection()

        user_game_play_data = {
            "gameDuration": self.input.total_time,
            "userId": user_id,
            "opponentId": opponent_id,
            "userScore": user_score,
            "opponentScore": opponent_score,
            "gameType": self.input.game_type,
            "rewardAmount": reward_amount
        }

        user_game_play_collection.insert_one(user_game_play_data)


    def compute(self):
        
        self._update_game_play(self.input.user_id, self.input.saarthi_id, self.input.user_score, self.input.saarthi_score, self.input.reward_amount)
        self._update_game_play(self.input.saarthi_id, self.input.user_id, self.input.saarthi_score, self.input.user_score, 0)

        return Output(
            output_details="",
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched game config"
        )