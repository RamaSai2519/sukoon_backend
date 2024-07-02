from models.interfaces import GetGameConfigInput as Input
from models.enum import GameType


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        game_type = self.input.game_type

        if game_type not in GameType.__members__:
            return False, "Game Type is wrong"
        return True, ""
    

    