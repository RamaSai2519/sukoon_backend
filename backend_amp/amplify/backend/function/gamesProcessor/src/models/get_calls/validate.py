from shared.models.interfaces import GetCallsInput as Input


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self) -> tuple:
        try:
            int(self.input.page)
            int(self.input.size)
        except (ValueError, TypeError):
            return False, "Page and size must be integers"

        if self.input.dest not in ["home", "graph", "list", "search"]:
            return False, "Invalid destination"

        return True, ""
