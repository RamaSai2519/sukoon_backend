from shared.models.interfaces import ScheduledJobInput as Input, Output
from db_queries.mutations.scheduled_job import create_scheduled_job
from shared.models.constants import OutputStatus


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input

    def compute(self) -> Output:

        create_scheduled_job(self.input.request_meta, self.input.status,
                             self.input.job_time, self.input.job_type, self.input.user_requested)

        return Output(
            output_details="",
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully created scheduled job"
        )
