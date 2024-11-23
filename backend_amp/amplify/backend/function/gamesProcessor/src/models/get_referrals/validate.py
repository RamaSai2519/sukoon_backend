from shared.models.interfaces import GetReferralsInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        input = self.input

        if not input.userId and not input.refCode:
            return False, "userId or refCode is required"

        if input.userId and input.refCode:
            return False, "Both userId and refCode cannot be provided together"

        return True, None
