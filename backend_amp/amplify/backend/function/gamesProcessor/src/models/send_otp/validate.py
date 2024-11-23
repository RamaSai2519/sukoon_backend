from shared.models.interfaces import SendOTPInput as Input


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        phone_number = self.input.phone_number

        if len(phone_number) != 10:
            return False, "INVALID PHONE NUMBER"
        return True, ""
