from shared.models.interfaces import User as Input
from shared.db.users import get_subscription_plans_collection, get_user_collection


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.plans_collection = get_subscription_plans_collection()

    def validate(self) -> tuple:
        for func in [self.validate_mandatory_fields, self.validate_field_types]:
            valid, message = func()
            if not valid:
                return False, message
        return True, ""

    def validate_field_types(self) -> tuple:
        bool_fields = ["active", "isBusy", "profileCompleted",
                       "wa_opt_out", "isPaidUser"]
        for field in bool_fields:
            if hasattr(self.input, field):
                value = getattr(self.input, field)
                if value is not None and not isinstance(value, bool):
                    return False, f"Field {field} must be a boolean"

        return True, ""

    def validate_mandatory_fields(self) -> tuple:
        if not self.input.phoneNumber and not self.input._id:
            return False, f"User Identifier is mandatory"

        if self.input.phoneNumber and len(self.input.phoneNumber) != 10:
            return False, f"Phone Number must be 10 digits"

        if self.input.plan and not self.plans_collection.find_one({"name": self.input.plan}):
            return False, f"Invalid Plan"

        return True, ""
