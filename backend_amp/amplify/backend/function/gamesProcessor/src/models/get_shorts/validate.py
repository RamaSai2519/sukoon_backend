from models.interfaces import UpdateGamePlayInput as Input
from models.enum import GameType


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):

        return True, ""
    

    