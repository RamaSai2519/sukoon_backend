from models.interfaces import EventInput as Input
from datetime import datetime


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_action(self):
        if self.input.action != "CREATE":
            return False, "Invalid action"
        return True, ""

    def validate_mandatory_fields(self):
        required_fields = {
            "slug": self.input.slug,
            "repeat": self.input.repeat,
            "imageUrl": self.input.imageUrl,
            "validUpto": self.input.validUpto,
            "eventType": self.input.eventType,
            "mainTitle": self.input.mainTitle,
            "guestSpeaker": self.input.guestSpeaker
        }

        print(required_fields)

        for field, value in required_fields.items():
            if not value:
                return False, f"{field} is required"

        return True, ""

    def validate_multiselect_fields(self):
        print(self.input.eventType)
        if self.input.eventType not in ["online", "offline", "not_event", "challenge"]:
            return False, "Invalid eventType"

        if self.input.repeat not in ["daily", "weekly", "monthly", "once", "yearly"]:
            return False, "Invalid repeat"

        return True, ""

    def validate_input(self):
        is_valid, message = self.validate_action()
        if not is_valid:
            return is_valid, message

        is_valid, message = self.validate_mandatory_fields()
        if not is_valid:
            return is_valid, message

        is_valid, message = self.validate_multiselect_fields()
        if not is_valid:
            return is_valid, message

        if len(self.input.slug) > 3:
            return False, "slug should be less than 3 characters"

        return True, ""
