from models.interfaces import GetUsersInput as Input
from models.constants import CallStatus


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input
        self.status_list = [
            value for name, value in CallStatus.__dict__.items() if not name.startswith('__')]

    def validate_input(self) -> tuple:
        if self.input.phoneNumber and len(self.input.phoneNumber) != 10:
            return False, "Invalid phone number"

        if self.input.call_status and self.input.call_status not in self.status_list:
            return False, "Invalid call status, must be one of: " + ", ".join(self.status_list)

        return True, ""
