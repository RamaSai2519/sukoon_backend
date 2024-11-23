from shared.models.interfaces import ScheduledJobInput as Input


class Validator:
    def __init__(self, input: Input):
        self.input = input

    def validate_input(self):
        if self.input.action == "UPDATE":
            return self.validate_update_input()
        elif self.input.action == "DELETE":
            return self.validate_delete_input()
        else:
            return False, "Invalid Action"

    def validate_update_input(self):
        if not self.input.scheduled_job_id:
            return False, "Scheduled Job ID is Mandatory"

        if not self.input.job_time:
            return False, "Job Time is Mandatory"

        return True, ""

    def validate_delete_input(self):
        if not self.input.scheduled_job_id:
            return False, "Scheduled Job ID is Mandatory"

        return True, ""
