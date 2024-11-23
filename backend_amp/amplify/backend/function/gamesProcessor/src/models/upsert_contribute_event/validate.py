from shared.models.interfaces import ContributeEvent as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self) -> tuple:
        mandatory_fields = ["name", "description", "validUpto", "image",
                            "locationType", "phoneNumber", "company"]
        if not self.input.slug:
            for field in mandatory_fields:
                if not getattr(self.input, field):
                    return False, f"{field} is mandatory"

        if self.input.locationType not in ["virtual", "on-site"]:
            return False, "Invalid locationType"

        return True, None
