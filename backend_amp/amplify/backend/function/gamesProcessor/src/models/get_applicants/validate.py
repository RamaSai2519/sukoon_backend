from models.interfaces import GetApplicantsInput as Input


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        if self.input.formType not in ["event", "sarathi"]:
            return False, "Invalid Form Type"

        return True, ""
