from models.interfaces import GetTimingsInput as Input
from bson import ObjectId


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        input = self.input

        if not input.expert:
            return False, "expert is required"

        try:
            ObjectId(input.expert)
        except:
            return False, "Invalid expert id"

        return True, None
