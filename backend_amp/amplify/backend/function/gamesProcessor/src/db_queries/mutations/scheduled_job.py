from helpers.base import call_graphql


def create_scheduled_job(request_meta, status, job_time, job_type) -> None:

    query = """
        mutation MyMutation($requestMeta: String, $scheduledJobStatus: ScheduledJobStatus, $scheduledJobTime: AWSDateTime, $scheduledJobType: ScheduledJobType) {
            createScheduledJobs(input: {requestMeta: $requestMeta, scheduledJobStatus: $scheduledJobStatus, scheduledJobTime: $scheduledJobTime, scheduledJobType: $scheduledJobType}) {
            id
            }
        }
    """
    params = {"requestMeta": request_meta, "scheduledJobStatus": status,
              "scheduledJobTime": job_time, "scheduledJobType": job_type}
    return call_graphql(query=query, params=params, message="create_scheduled_job")


def update_scheduled_job(variables):
    query = """
    mutation MyMutation($input: UpdateScheduledJobsInput!) {
      updateScheduledJobs(input: $input) {
        id
        scheduledJobTime
      }
    }
    """
    return call_graphql(query=query, params=variables, message="update_scheduled_job")
