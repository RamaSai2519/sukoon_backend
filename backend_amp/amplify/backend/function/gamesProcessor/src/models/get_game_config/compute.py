from configs import CONFIG as config
from models.interfaces import GetGameConfigInput as Input, Output
from models.constants import OutputStatus
from db.games import get_games_config_collection

class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input
 

    def _get_game_config(self) -> dict:
        games_config_collection = get_games_config_collection()
        games_config_collection.create_index([("gameType")])
        game_config = list(games_config_collection.find({"gameType": self.input.game_type}, {"_id": 0}))
        return game_config

    def compute(self):

        game_config = self._get_game_config()

        return Output(
            output_details= {"game_config": game_config},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched game config"
        )