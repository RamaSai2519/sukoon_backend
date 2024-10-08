from models.interfaces import GetUsersInput as Input


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        if self.input.phoneNumber and len(self.input.phoneNumber) != 10:
            return False, "Invalid phone number"

        return True, ""
