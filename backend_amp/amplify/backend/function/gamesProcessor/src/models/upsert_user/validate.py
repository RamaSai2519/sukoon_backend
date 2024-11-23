from shared.models.interfaces import User as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate(self):
        for func in [self.validate_mandatory_fields, self.validate_field_types]:
            valid, message = func()
            if not valid:
                return False, message
        return True, ""

    def validate_field_types(self):
        bool_fields = ["active", "isBusy", "profileCompleted",
                       "wa_opt_out", "isBlocked", "isPaidUser"]
        for field in bool_fields:
            if hasattr(self.input, field):
                value = getattr(self.input, field)
                if value is not None and not isinstance(value, bool):
                    return False, f"Field {field} must be a boolean"

        int_fields = ["numberOfGames", "numberOfCalls"]
        for field in int_fields:
            if hasattr(self.input, field):
                value = getattr(self.input, field)
                if value is not None and not isinstance(value, int):
                    return False, f"Field {field} must be an integer"
        return True, ""

    def validate_mandatory_fields(self):
        if not self.input.phoneNumber and not self.input._id:
            return False, f"User Identifier is mandatory"

        if self.input.phoneNumber and len(self.input.phoneNumber) != 10:
            return False, f"Phone Number must be 10 digits"

        return True, ""
