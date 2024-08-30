from models.interfaces import ValidateOTPInput as Input
from models.enum import GameType


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        if len(self.input.phone_number) != 10:
            return False, "INVALID PHONE NUMBER"

        if self.input.user_type not in ["user", "expert"]:
            return False, "INVALID USER TYPE"
        return True, ""
