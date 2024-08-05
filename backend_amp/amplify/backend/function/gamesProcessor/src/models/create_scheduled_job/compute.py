from models.interfaces import CreateScheduledJobInput as Input, Output
from models.constants import OutputStatus
from db_queries.mutations.scheduled_job import create_scheduled_job, delete_scheduled_job

class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input

    def compute(self):

        if self.input.action == "CREATE":

            create_scheduled_job(self.input.request_meta, self.input.status, self.input.job_time,  self.input.job_type)
            
        else:
            delete_scheduled_job(self.input.scheduled_job_id)

        return Output(
            output_details="",
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully created scheduled job"
        )