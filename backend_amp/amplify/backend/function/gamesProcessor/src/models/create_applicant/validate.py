from models.interfaces import ApplicantInput as Input


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        if self.input.formType not in ["event", "sarathi"]:
            return False, "Invalid Form Type"

        if len(self.input.phoneNumber) != 10:
            return False, "Invalid Phone Number"

        if str(self.input.gender).lower() not in ["male", "female", "notSay"]:
            return False, "Invalid Gender"

        return True, ""
