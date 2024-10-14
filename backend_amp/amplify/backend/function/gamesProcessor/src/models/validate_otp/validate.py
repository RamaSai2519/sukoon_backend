from models.interfaces import ValidateOTPInput as Input
from models.constants import CallStatus


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input
        self.status_list = [
            value for name, value in CallStatus.__dict__.items() if not name.startswith('__')]

    def validate_input(self):
        if len(self.input.phone_number) != 10:
            return False, "INVALID PHONE NUMBER"

        if self.input.user_type not in ["user", "expert"]:
            return False, "INVALID USER TYPE"

        if self.input.call_status not in self.status_list:
            return False, "Invalid call status, must be one of: " + ", ".join(self.status_list)

        return True, ""
