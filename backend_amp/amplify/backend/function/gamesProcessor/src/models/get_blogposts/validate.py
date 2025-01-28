from shared.models.interfaces import GetBlogPostsInput as Input

class Validate:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self) -> tuple:
        
        if self.input.page is not None and (not isinstance(self.input.page, int) or self.input.page < 0):
            return False, "Page must be a non-negative integer."

        if self.input.size is not None and (not isinstance(self.input.size, int) or self.input.size <= 0):
            return False, "Size must be a positive integer."

        if self.input.tags and not isinstance(self.input.tags, list):
            return False, "Tags must be a list of strings."

        return True, ""
