from models.interfaces import GetGamePlayInput as Input, Output
from models.constants import OutputStatus
from db.users import get_user_game_plays_collection

class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input


    def _get_game_play(self) -> dict:

        user_game_play_collection = get_user_game_plays_collection()
        user_game_plays = list(user_game_play_collection.find({"userId": self.input.user_id}, {"_id": 0}))

        return user_game_plays


    def compute(self):
        
        user_game_plays = self._get_game_play()

        return Output(
            output_details={"user_game_plays": user_game_plays},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched game config"
        )