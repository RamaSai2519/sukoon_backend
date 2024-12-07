from shared.models.interfaces import UpsertRecurringSchedulesInput as Input
from shared.models.constants import TimeFormats, re_frequencies
from datetime import datetime
from bson import ObjectId


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_ids(self) -> tuple:
        try:
            ObjectId(self.input.user_id)
            ObjectId(self.input.expert_id)
        except Exception:
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

    def validate_frequency(self) -> tuple:
        if self.input.frequency not in re_frequencies:
            return False, "Invalid type"

        if self.input.frequency == 'weekly' and (not self.input.week_days or self.input.month_days):
            return False, "Week days required for weekly frequency"

        if self.input.frequency == 'monthly' and (not self.input.month_days or self.input.week_days):
            return False, "Month days required for monthly frequency"

        if self.input.frequency == 'daily' and (self.input.week_days or self.input.month_days):
            return False, "Week days and month days not required for daily frequency"

        if self.input.week_days:
            days = ['monday', 'tuesday', 'wednesday',
                    'thursday', 'friday', 'saturday', 'sunday']
            for day in self.input.week_days:
                if day not in days:
                    return False, f"Invalid day: {day}"

        if self.input.month_days:
            for day in self.input.month_days:
                if day < 1 or day > 31:
                    return False, f"Invalid day: {day}"

        return True, ""

    def validate_type(self) -> tuple:
        types = ['WA', 'CALL']
        if self.input.job_type not in types:
            return False, "Invalid type"
        return True, ""

    def validate_input(self) -> tuple:
        for func in [self.validate_ids, self.validate_frequency, self.validate_times, self.validate_type]:
            valid, message = func()
            if not valid:
                return False, message
        return True, ""
