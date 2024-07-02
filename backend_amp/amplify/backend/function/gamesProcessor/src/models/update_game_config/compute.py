
from models.interfaces import UpdateGameConfigInput as Input, Output
from models.constants import OutputStatus
from db.games import get_games_config_collection


class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input
 
    def _update_game_config(self) -> None:
        game_config = self.input.game_config
        level = game_config.get("level")
        game_config["gameType"] = self.input.game_type

        games_config_collection = get_games_config_collection()
        games_config_collection.create_index([("gameType")])
        game_config_db = games_config_collection.find_one({"gameType": self.input.game_type, "level": level})

        if game_config_db:
            games_config_collection.replace_one(
                    {"_id": game_config_db["_id"]},
                    game_config
                )
        else:
            games_config_collection.insert_one(game_config)


    def compute(self):
        self._update_game_config()

        return Output(
            output_details= {"game_config": ""},
            output_status=OutputStatus.SUCCESS,
            output_message="OTP Authentication Successful"
        )