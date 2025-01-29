from shared.models.interfaces import GetBlogPostsInput as Input

class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        try:
            int(self.input.page)
            int(self.input.size)
        except:
            return False, "Page and size must be integers"

        return True, ""
