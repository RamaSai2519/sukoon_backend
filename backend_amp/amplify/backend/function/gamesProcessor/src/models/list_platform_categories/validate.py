from shared.models.interfaces import ListPlatformCategoriesInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        if self.input.type and self.input.type not in ['main', 'sub']:
            return False, "Invalid type"

        return True, ""
