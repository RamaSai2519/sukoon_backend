from shared.models.interfaces import UpsertRefTokenInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        if ' ' in self.input.token or ' ' in self.input.name:
            return False, "Token and Name cannot contain spaces"

        return True, ""
