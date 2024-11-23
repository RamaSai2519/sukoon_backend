from shared.models.interfaces import ApplicantInput as Input


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        if self.input.formType not in ["event", "sarathi", "ambassador"]:
            return False, "Invalid Form Type"

        if len(self.input.phoneNumber) != 10:
            return False, "Invalid Phone Number"

        if str(self.input.gender).lower() not in ["male", "female", "notSay"]:
            return False, "Invalid Gender"

        valid, error = self.validate_required_fields()
        if not valid:
            return False, error

        return True, ""

    def validate_required_fields(self):
        for attr, value in self.input.__dict__.items():
            if value == '' or value == []:
                return False, f"{attr} is required"
        return True, ""
