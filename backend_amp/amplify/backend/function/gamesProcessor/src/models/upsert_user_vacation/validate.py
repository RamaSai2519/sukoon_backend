from shared.models.interfaces import UpsertUserVacationInput as Input
from shared.models.constants import TimeFormats
from shared.models.common import Common
from datetime import datetime
from bson import ObjectId
import pytz


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_start_data(self) -> bool:
        start_date = datetime.strptime(self.input.start_date,
                                       TimeFormats.ANTD_TIME_FORMAT)
        start_date = start_date.replace(tzinfo=pytz.utc)
        current_time = Common.get_current_utc_time()
        if start_date < current_time:
            return False, "Start date cannot be in the past"
        return True, ""

    def validate_input(self) -> tuple:
        try:
            ObjectId(self.input.user)
        except:
            return False, "Invalid user ID"

        try:
            fields = ['start_date', 'end_date']
            for field in fields:
                date = getattr(self.input, field)
                datetime.strptime(date, TimeFormats.ANTD_TIME_FORMAT)
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

        # valid, message = self.validate_start_data()
        # if not valid:
        #     return valid, message

        return True, ""
