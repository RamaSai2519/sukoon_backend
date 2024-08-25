from models.interfaces import GetExpertsInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        if self.input.phoneNumber and len(self.input.phoneNumber) != 10:
            return False, "Invalid phone number"

        if self.input.schedule_status and self.input.schedule_status not in ["pending", "completed", "missed"]:
            return False, "Invalid schedule status"

        return True, ""
