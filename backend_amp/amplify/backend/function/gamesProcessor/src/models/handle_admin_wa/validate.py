from models.interfaces import AdminWaInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.userTypes = ["partial", "full", "all", "event"]

    def validate_input(self):
        if self.input.action not in ["preview", "send"]:
            return False, "Invalid action"

        if not self.input.usersType and not self.input.cities:
            return False, "Neither User Type or User Cities are provided"

        if self.input.usersType and self.input.usersType not in self.userTypes:
            return False, "Invalid User Type"

        if self.input.usersType and self.input.cities:
            return False, "Both User Type and User Cities are provided"

        if self.input.usersType == "event" and not self.input.eventId:
            return False, "Event slug is required"

        return True, ""
