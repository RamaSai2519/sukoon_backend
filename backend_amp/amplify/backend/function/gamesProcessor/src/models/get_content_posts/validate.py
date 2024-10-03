from models.interfaces import GetContentPostsInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self) -> tuple:
        try:
            int(self.input.page)
            int(self.input.size)
        except (ValueError, TypeError):
            return False, "Page and size must be integers"
        return True, ""
