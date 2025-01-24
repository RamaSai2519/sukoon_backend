from shared.models.interfaces import ValidatePRCInput as Input
from bson import ObjectId


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        try:
            ObjectId(self.input.user_id)
        except Exception:
            return False, "Invalid User Id"

        return True, ""
