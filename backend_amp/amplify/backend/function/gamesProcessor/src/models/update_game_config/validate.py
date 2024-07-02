from models.interfaces import UpdateGameConfigInput as Input
from models.enum import GameType

class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        game_config = self.input.game_config
        game_type = self.input.game_type

        if game_type not in GameType.__members__:
            return False, "Game Type is wrong"

        level = game_config.get("level")
        if not level or level <=0:
            return False, "Level should be greater than 0"
        
        return True, ""
    