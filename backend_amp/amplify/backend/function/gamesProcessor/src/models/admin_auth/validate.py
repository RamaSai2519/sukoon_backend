from shared.models.interfaces import AdminAuthInput as Input


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self) -> tuple:
        if self.input.action not in ["login", "register", "refresh"]:
            return False, "Invalid action"

        if self.input.action == "login":
            if not self.input.phoneNumber or not self.input.password:
                return False, "Missing Phone Number or Password"

        if self.input.action == "register":
            if not self.input.phoneNumber or not self.input.password or not self.input.name:
                return False, "Missing Phone Number or Password or Name"
            if self.input.access_level not in ["basic", "admin", "super"]:
                return False, "Invalid access level"

        return True, ""
