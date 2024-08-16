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
            "eventEndTime": self.input.eventEndTime,
            "eventType": self.input.eventType,
            "imageUrl": self.input.imageUrl,
            "mainTitle": self.input.mainTitle,
            "repeat": self.input.repeat,
            "slug": self.input.slug,
            "guestSpeaker": self.input.guestSpeaker,
            "isPremiumUserOnly": self.input.isPremiumUserOnly
        }

        for field, value in required_fields.items():
            if not value:
                return False, f"{field} is required"

        return True, ""

    def validate_time_fields(self):
        try:
            datetime.strptime(self.input.eventEndTime, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            return False, "eventEndTime is not a valid AWS time string"

        if self.input.eventStartTime:
            try:
                datetime.strptime(self.input.eventStartTime,
                                  '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                return False, "eventStartTime is not a valid AWS time string"

        if self.input.registrationAllowedTillTime:
            try:
                datetime.strptime(
                    self.input.registrationAllowedTillTime, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                return False, "registrationAllowedTillTime is not a valid AWS time string"

        return True, ""

    def validate_multiselect_fields(self):
        print(self.input.eventType)
        if self.input.eventType not in ["SESSION", "CHALLENGE"]:
            return False, "Invalid eventType"

        if self.input.repeat not in ["Daily", "Weekly", "Monthly", "Once"]:
            return False, "Invalid repeat"

        return True, ""

    def validate_input(self):
        is_valid, message = self.validate_action()
        if not is_valid:
            return is_valid, message

        is_valid, message = self.validate_mandatory_fields()
        if not is_valid:
            return is_valid, message

        is_valid, message = self.validate_time_fields()
        if not is_valid:
            return is_valid, message

        is_valid, message = self.validate_multiselect_fields()
        if not is_valid:
            return is_valid, message

        return True, ""
