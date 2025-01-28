from shared.models.interfaces import UpsertUserVacationInput as Input
from shared.models.constants import TimeFormats
from datetime import datetime
from bson import ObjectId


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self) -> tuple:
        try:
            ObjectId(self.input.user)
        except:
            return False, "Invalid user ID"

        try:
            fields = ['start_date', 'end_date']
            for field in fields:
                datetime.strptime(getattr(self.input, field),
                                  TimeFormats.ANTD_TIME_FORMAT)
        except:
            return False, "Invalid date(s)"

        try:
            fields = ['start_time', 'end_time']
            for field in fields:
                datetime.strptime(getattr(self.input, field),
                                  TimeFormats.HOURS_24_FORMAT)
        except:
            return False, "Invalid time(s)"

        if self.input.user_type not in ['user', 'expert']:
            return False, "Invalid user type"

        return True, ""
