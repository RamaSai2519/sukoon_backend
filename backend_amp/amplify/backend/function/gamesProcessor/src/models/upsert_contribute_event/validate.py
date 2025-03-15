from shared.models.interfaces import ContributeEvent as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self) -> tuple:
        if self.input.isDeleted == True and not self.input.slug:
            return False, "slug is required to delete"
        elif self.input.isDeleted == True:
            return True, ""

        mandatory_fields = ["name", "description", "validUpto", "image",
                            "locationType", "phoneNumber", "company"]
        if not self.input.slug:
            for field in mandatory_fields:
                if not getattr(self.input, field):
                    return False, f"{field} is mandatory"

        if self.input.locationType not in ["virtual", "on-site"]:
            return False, "Invalid locationType"

        if not isinstance(self.input.isSukoon, bool):
            return False, "Invalid isSukoon"

        return True, None
