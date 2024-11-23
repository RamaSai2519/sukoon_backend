from shared.helpers.base import call_graphql


def create_scheduled_job(request_meta, status, job_time, job_type, user_requested=None) -> None:

    query = """
    mutation MyMutation($requestMeta: String, $scheduledJobStatus: ScheduledJobStatus, $scheduledJobTime: AWSDateTime, $scheduledJobType: ScheduledJobType, $user_requested: Boolean) {
      createScheduledJobs(input: {requestMeta: $requestMeta, scheduledJobStatus: $scheduledJobStatus, scheduledJobTime: $scheduledJobTime, scheduledJobType: $scheduledJobType, user_requested: $user_requested}) {
        id
      }
    }
    """
    params = {"requestMeta": request_meta, "scheduledJobStatus": status,
              "scheduledJobTime": job_time, "scheduledJobType": job_type, "user_requested": user_requested}
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


def update_scheduled_job_status(job_id, status):
    query = """
        mutation MyMutation2($id: ID!, $status: String) {
            updateScheduledJobs(input: {id: $id, status: $status}) {
                id
            }
        }
    """
    params = {"id": job_id, "status": status}
    return call_graphql(query=query, params=params, message="update_scheduled_job_status")
