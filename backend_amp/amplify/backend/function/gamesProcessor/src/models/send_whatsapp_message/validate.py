from shared.models.interfaces import WhtasappMessageInput as Input


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):

        if not self.input.template_name:
            return False, "Template Name is Required Field"

        if not self.input.phone_number:
            return False, "Phone Number is Required Field"

        if len(self.input.phone_number) != 10:
            return False, "Phone number is not correct"

        return True, ""
