from shared.models.interfaces import GetEventUsersInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        try:
            int(self.input.page)
            int(self.input.size)
        except Exception:
            return False, 'Page and Size should be int'
        return True, ""
