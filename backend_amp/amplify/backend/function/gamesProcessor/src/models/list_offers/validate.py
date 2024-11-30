from shared.models.interfaces import ListOffersInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        try:
            int(self.input.page)
            int(self.input.size)
        except (ValueError, TypeError):
            return False, "Page and size must be integers"

        try:
            bool(self.input.include_expired)
        except ValueError:
            return False, "Include expired must be a boolean"

        return True, ""
