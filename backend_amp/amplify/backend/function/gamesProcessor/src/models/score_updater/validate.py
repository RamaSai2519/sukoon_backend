from shared.models.interfaces import QuizGameInput as Input
from models.enum import GameType


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):

        return True, ""
