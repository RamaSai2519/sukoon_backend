from bson import ObjectId
from shared.models.interfaces import CreateClubInterestInput as Input


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        try:
            ObjectId(self.input.user_id)
        except:
            return False, "Invalid User ID"

        return True, ""
