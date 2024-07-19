from helpers.base import call_graphql


def get_pending_scheduled_jobs(status, time, next_token):
    query = """
        query MyQuery($scheduledJobStatus: ScheduledJobStatus, $le: String, , $nextToken: String) {
            scheduledJobsByStatusAndTime(scheduledJobStatus: $scheduledJobStatus, scheduledJobTime: {le: $le}, nextToken: $nextToken) {
                items {
                    request_meta
                    scheduledJobStatus
                    scheduledJobTime
                    scheduledJobType
                }
            }
        }
    """
    params = {"scheduledJobStatus": status, "le": time, "nextToken": next_token}
    return call_graphql(query=query , params=params, message="get_pending_scheduled_jobs")


def mark_my_job_as_picked(job_id):
    query = """
        mutation MyMutation2($id: ID!, $scheduledJobStatus: ScheduledJobStatus) {
            updateScheduledJobs(input: {id: $id, scheduledJobStatus: $scheduledJobStatus}) {
                id
            }
        }
    """
    params = {"id": job_id, "scheduledJobStatus": "PICKED"}
    return call_graphql(query=query , params=params, message="mark_my_job_as_picked")