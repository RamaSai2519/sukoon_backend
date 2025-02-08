from shared.models.interfaces import RecordAdClickInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        if self.input.user_age and not self.input.user_age.isdigit():
            return False, "Invalid user_age"

        return True, ""
