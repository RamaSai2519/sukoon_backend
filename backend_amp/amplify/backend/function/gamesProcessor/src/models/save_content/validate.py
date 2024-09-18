from models.interfaces import SaveContentInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):

        return True, ""
