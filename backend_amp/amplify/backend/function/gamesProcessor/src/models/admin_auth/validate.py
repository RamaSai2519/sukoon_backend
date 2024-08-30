from models.interfaces import AdminAuthInput as Input


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        if self.input.action not in ["login", "register", "refresh"]:
            return False, "Invalid action"

        if self.input.action == "login":
            if not self.input.phoneNumber or not self.input.password:
                return False, "Missing Phone Number or Password"

        if self.input.action == "register":
            if not self.input.phoneNumber or not self.input.password or not self.input.name:
                return False, "Missing Phone Number or Password or Name"

        return True, ""
