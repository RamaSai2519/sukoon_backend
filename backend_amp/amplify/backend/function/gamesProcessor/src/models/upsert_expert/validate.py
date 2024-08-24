from models.interfaces import Expert as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate(self):
        for func in [self.validate_mandatory_fields, self.validate_field_types, self.validate_multiselect_fields, self.validate_url_fields]:
            valid, message = func()
            if not valid:
                return False, message
        return True, ""

    def validate_field_types(self):
        bool_fields = ["active", "isBusy", "profileCompleted"]
        for field in bool_fields:
            if hasattr(self.input, field):
                value = getattr(self.input, field)
                if value is not None and not isinstance(value, bool):
                    return False, f"Field {field} must be a boolean"
        return True, ""

    def validate_multiselect_fields(self):
        if hasattr(self.input, "status"):
            if self.input.status is not None and self.input.status not in ["offline", "online"]:
                return False, "Field status must be either 'offline' or 'online'"
        if hasattr(self.input, "type"):
            if self.input.type is not None and self.input.type not in ["sarathi", "expert"]:
                return False, "Field type must be either 'sarathi' or 'expert'"
        return True, ""

    def validate_url_fields(self):
        url_fields = ["video", "profile"]
        for field in url_fields:
            if hasattr(self.input, field):
                value = getattr(self.input, field)
                if value is not None and not str(value).startswith("http"):
                    return False, f"Field {field} must be a valid URL"
        return True, ""

    def validate_mandatory_fields(self):
        if not self.input.phoneNumber:
            return False, f"Phone Number is mandatory"
        return True, ""
