from models.interfaces import CreateScheduledJobInput as Input, Output
from models.constants import OutputStatus
from helpers.base import call_graphql


class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input


    def _create_scheduled_job(self) -> None:

        query = """
            mutation MyMutation($request_meta: String, $scheduledJobStatus: ScheduledJobStatus, $scheduledJobTime: AWSDateTime, $scheduledJobType: ScheduledJobType) {
                createScheduledJobs(input: {request_meta: $request_meta, scheduledJobStatus: $scheduledJobStatus, scheduledJobTime: $scheduledJobTime, scheduledJobType: $scheduledJobType}) {
                id
                }
            }
        """
        params = {"request_meta": self.input.request_meta, "scheduledJobStatus": self.input.status, "scheduledJobTime": self.input.job_time, "scheduledJobType": self.input.job_type}
        return call_graphql(query=query , params=params, message="create_scheduled_job")


    def compute(self):
        
        self._create_scheduled_job()

        return Output(
            output_details="",
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully created scheduled job"
        )