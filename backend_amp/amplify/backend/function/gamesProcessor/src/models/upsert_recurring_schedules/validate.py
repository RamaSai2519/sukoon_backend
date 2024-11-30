from shared.models.interfaces import UpsertRecurringSchedulesInput as Input
from shared.models.constants import TimeFormats
from datetime import datetime
from bson import ObjectId


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_ids(self) -> tuple:
        try:
            ObjectId(self.input.user_id)
            ObjectId(self.input.expert_id)
        except Exception as e:
            return False, "Invalid user_id or expert_id"
        return True, ""

    def validate_times(self) -> tuple:
        ant_format = TimeFormats.ANTD_TIME_FORMAT
        try:
            datetime.strptime(self.input.job_expiry, ant_format)
            datetime.strptime(self.input.job_time, TimeFormats.HOURS_24_FORMAT)
        except Exception as e:
            return False, "Invalid time format"
        return True, ""

    def validate_days(self) -> tuple:
        days = ['monday', 'tuesday', 'wednesday',
                'thursday', 'friday', 'saturday', 'sunday']
        for day in self.input.days:
            if day not in days:
                return False, f"Invalid day: {day}"
        return True, ""

    def validate_frequency(self) -> tuple:
        frequencies = ['weekly', 'monthly', 'biweekly']
        if self.input.frequency not in frequencies:
            return False, "Invalid type"
        return True, ""

    def validate_type(self) -> tuple:
        types = ['WA', 'CALL']
        if self.input.job_type not in types:
            return False, "Invalid type"
        return True, ""

    def validate_input(self) -> tuple:
        for func in [self.validate_ids, self.validate_times, self.validate_days, self.validate_frequency, self.validate_type]:
            valid, message = func()
            if not valid:
                return False, message
        return True, ""
