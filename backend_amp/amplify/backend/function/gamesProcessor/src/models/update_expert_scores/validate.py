from shared.models.interfaces import Expert as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate(self) -> tuple:

        return True, ""
