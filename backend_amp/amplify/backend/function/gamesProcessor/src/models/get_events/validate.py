from models.interfaces import GetEventsInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        try:
            int(self.input.page)
        except ValueError:
            return False, "Page should be an integer"

        try:
            int(self.input.limit)
        except ValueError:
            return False, "Limit should be an integer"

        if self.input.fromToday.lower() not in ["true", "false"]:
            return False, "fromToday should be a boolean"

        if self.input.isHomePage.lower() not in ["true", "false"]:
            return False, "isHomePage should be a boolean"

        return True, ""
