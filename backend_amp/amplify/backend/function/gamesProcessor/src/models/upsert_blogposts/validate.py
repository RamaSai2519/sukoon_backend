class UpsertValidator:
    def __init__(self, input: input) -> None:
        self.input = input

    def validate_input(self):
        if not self.input.title:
            return False, "Title is required."

        if self.input.title and len(self.input.title)>100:
            return False, "Title must not exceed 100 characters."

        if not self.input.body:
            return False, "Body content is required."

        if self.input.meta_description and len(self.input.meta_description) > 160:
            return False, "Meta description must not exceed 160 characters."

        if not self.input.phoneNumber.isdigit() or len(self.input.phoneNumber) != 10:
            return False, "Phone number must be a 10-digit numeric value."

        return True, ""
