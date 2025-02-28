from shared.models.interfaces import GetQuizQuestionsInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self) -> tuple:
        if self.input.page and self.input.size:
            try:
                int(self.input.page)
                int(self.input.size)
            except:
                return False, "Invalid size or page"

        return True, ""
