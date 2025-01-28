from shared.models.interfaces import BlogPostInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):

        if self.input.title and len(self.input.title) > 100:
            return False, "Title must not exceed 100 characters."

        return True, ""
