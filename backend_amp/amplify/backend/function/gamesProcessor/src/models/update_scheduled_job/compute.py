from models.constants import OutputStatus
from models.interfaces import ScheduledJobInput as Input, Output
from db_queries.mutations.scheduled_job import update_scheduled_job, delete_scheduled_job


class Compute:
    def __init__(self, input: Input):
        self.input = input

    def compute(self):
        if self.input.action == "UPDATE":
            return self._update_scheduled_job()
        elif self.input.action == "DELETE":
            return self._delete_scheduled_job()
        else:
            return Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message="Invalid action"
            )

    def _update_scheduled_job(self):
        variables = {
            "input": {
                "id": self.input.scheduled_job_id,
                "scheduledJobTime": self.input.job_time
            }
        }
        response = update_scheduled_job(variables)

        return Output(
            output_details=response,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully updated scheduled job"
        )

    def _delete_scheduled_job(self):
        response = update_scheduled_job({
            "input": {
                "id": self.input.scheduled_job_id,
                "isDeleted": True
            }
        })

        return Output(
            output_details=response,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully deleted scheduled job"
        )
