from models.interfaces import ScheduledJobInput as Input
from datetime import datetime


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input

    def validate_input(self):
        is_valid, message = self.validate_action()
        if not is_valid:
            return is_valid, message

        is_valid, message = self.validate_mandatory_fields()
        if not is_valid:
            return is_valid, message

        is_valid, message = self.validate_job_time_and_status()
        if not is_valid:
            return is_valid, message

        return True, ""

    def validate_action(self):
        if self.input.action != "CREATE":
            return False, "Action must be 'CREATE'"
        return True, ""

    def validate_mandatory_fields(self):
        if not self.input.job_time:
            return False, "Job time is mandatory"
        if not self.input.job_type:
            return False, "Job type is mandatory"
        if not self.input.status:
            return False, "Status is mandatory"
        if not self.input.request_meta:
            return False, "Request meta is mandatory"
        return True, ""

    def validate_job_time_and_status(self):
        try:
            datetime.strptime(self.input.job_time, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            return False, "Job time is not a valid AWS time string"

        if self.input.status != "PENDING":
            return False, "Status must be 'PENDING'"

        return True, ""
