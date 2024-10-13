from models.interfaces import ScheduledJobInput as Input
from datetime import datetime


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        is_valid, message = self.validate_mandatory_fields()
        if not is_valid:
            return is_valid, message

        is_valid, message = self.validate_job_time_and_status()
        if not is_valid:
            return is_valid, message

        return True, ""

    def validate_mandatory_fields(self):
        mandatory_fields = ['job_time', 'job_type', 'status', 'request_meta']
        for field in mandatory_fields:
            if not getattr(self.input, field):
                return False, f"{field.replace('_', ' ').capitalize()} is mandatory"
        return True, ""

    def validate_job_time_and_status(self):
        try:
            datetime.strptime(self.input.job_time, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            return False, "Job time is not a valid AWS time string"

        if self.input.status not in ['PENDING', 'WAPENDING']:
            return False, "Invalid status"

        return True, ""
