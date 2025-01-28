from shared.models.interfaces import GetBetaTestersInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        try:
            int(self.input.page)
            int(self.input.size)
        except:
            return False, "page and size should be integers"

        return True, ""
