from shared.models.interfaces import WaOptionsInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        if self.input.type not in ["form"]:
            return False, "Invalid type"

        return True, ""
