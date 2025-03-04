from shared.models.interfaces import RecordAdClickInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        try:
            int(self.input.user_age)
        except:
            return False, "Invalid user_age"

        return True, ""
