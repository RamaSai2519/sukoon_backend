from shared.models.interfaces import GetTimingsInput as Input
from bson import ObjectId


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):

        return True, None
