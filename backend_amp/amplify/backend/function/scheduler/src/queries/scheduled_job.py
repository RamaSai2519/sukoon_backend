from helpers.base import call_graphql

def get_pending_scheduled_jobs(status, time, next_token):

    if not next_token:

        query = """
            query MyQuery($scheduledJobStatus: ScheduledJobStatus!, $le: String) {
                scheduledJobsByStatusAndTime(scheduledJobStatus: $scheduledJobStatus, scheduledJobTime: {le: $le}) {
                    nextToken
                    items {
                        id
                        requestMeta
                        scheduledJobStatus
                        scheduledJobTime
                        scheduledJobType
                    }
                }
            }
        """
        params = {"scheduledJobStatus": status, "le": time}

    else:

        query = """
            query MyQuery($scheduledJobStatus: ScheduledJobStatus!, $le: String, $nextToken: String) {
                scheduledJobsByStatusAndTime(scheduledJobStatus: $scheduledJobStatus, scheduledJobTime: {le: $le}, nextToken: $nextToken) {
                    nextToken
                    items {
                        id
                        requestMeta
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


def update_scheduled_job_status(job_id, status):
    query = """
        mutation MyMutation2($id: ID!, $status: String) {
            updateScheduledJobs(input: {id: $id, status: $status}) {
                id
            }
        }
    """
    params = {"id": job_id, "status": status}
    return call_graphql(query=query , params=params, message="update_scheduled_job_status")