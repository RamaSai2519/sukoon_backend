from shared.models.interfaces import GetSlotsInput as Input
from shared.models.constants import TimeFormats
from datetime import datetime
from bson import ObjectId


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        if not self._is_valid_duration():
            return False, "Duration should be an integer"

        if not self._is_valid_expert_id():
            return False, "Invalid expert id"

        if not self._is_valid_datetime():
            return False, "Invalid datetime"

        return True, ""

    def _is_valid_duration(self):
        try:
            int(self.input.duration)
            return True
        except ValueError:
            return False

    def _is_valid_expert_id(self):
        try:
            ObjectId(self.input.expert)
            return True
        except Exception:
            return False

    def _is_valid_datetime(self):
        try:
            datetime.strptime(self.input.datetime,
                              TimeFormats.ANTD_TIME_FORMAT)
            return True
        except ValueError:
            return False
