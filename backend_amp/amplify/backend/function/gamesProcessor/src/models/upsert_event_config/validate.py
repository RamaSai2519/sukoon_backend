from models.interfaces import Event as Input
from flask_jwt_extended import jwt_required


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_mandatory_fields(self) -> tuple:
        required_fields = {
            "slug": self.input.slug,
            "repeat": self.input.repeat,
            "imageUrl": self.input.imageUrl,
            "validUpto": self.input.validUpto,
            "eventType": self.input.eventType,
            "mainTitle": self.input.mainTitle,
            "guestSpeaker": self.input.guestSpeaker
        }

        for field, value in required_fields.items():
            if not value:
                return False, f"{field} is required"

        return True, ""

    def validate_multiselect_fields(self):
        if self.input.eventType not in ["online", "offline", "not_event", "challenge"]:
            return False, "Invalid eventType"

        if self.input.repeat not in ["daily", "weekly", "monthly", "once", "yearly"]:
            return False, "Invalid repeat"

        return True, ""

    @jwt_required()
    def require_jwt(self) -> None:
        pass

    def validate_input(self) -> tuple:
        if self.input.isDeleted == True and not self.input.slug:
            return False, "slug is required to delete"
        elif self.input.isDeleted == True:
            self.require_jwt()
            return True, ""

        is_valid, message = self.validate_mandatory_fields()
        if not is_valid:
            return is_valid, message

        is_valid, message = self.validate_multiselect_fields()
        if not is_valid:
            return is_valid, message

        if len(self.input.slug) > 3:
            return False, "slug should be less than 3 characters"

        return True, ""
