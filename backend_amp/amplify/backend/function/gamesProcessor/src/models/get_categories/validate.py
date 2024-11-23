from shared.models.interfaces import CategoriesInput as Input


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self) -> tuple:
        if self.input.action not in ["get", "post"]:
            return False, "Invalid action"

        return True, ""
