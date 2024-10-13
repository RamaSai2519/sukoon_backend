from datetime import datetime, timedelta
from helpers.base import call_graphql


def get_pending_scheduled_jobs(status, time, next_token):

    if not next_token:

        query = """
            query MyQuery($scheduledJobStatus: ScheduledJobStatus!, $le: String) {
                scheduledJobsByStatusAndTime(scheduledJobStatus: $scheduledJobStatus, filter: {isDeleted: {ne: true}}, limit: 1000, scheduledJobTime: {le: $le}) {
                    nextToken
                    items {
                        id
                        requestMeta
                        user_requested
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
                scheduledJobsByStatusAndTime(scheduledJobStatus: $scheduledJobStatus, filter: {isDeleted: {ne: true}}, limit: 1000, scheduledJobTime: {le: $le}, nextToken: $nextToken) {
                    nextToken
                    items {
                        id
                        user_requested
                        requestMeta
                        scheduledJobStatus
                        scheduledJobTime
                        scheduledJobType
                    }
                }
            }
        """
        params = {"scheduledJobStatus": status, "le": time, "nextToken": next_token}
    return call_graphql(query=query, params=params, message="get_pending_scheduled_jobs")


def mark_my_job_as_picked(job_id):
    query = """
        mutation MyMutation2($id: ID!, $scheduledJobStatus: ScheduledJobStatus) {
            updateScheduledJobs(input: {id: $id, scheduledJobStatus: $scheduledJobStatus}) {
                id
            }
        }
    """
    params = {"id": job_id, "scheduledJobStatus": "PICKED"}
    return call_graphql(query=query, params=params, message="mark_my_job_as_picked")


def mark_my_job_as_pending(job_id):
    query = """
        mutation MyMutation2($id: ID!, $scheduledJobStatus: ScheduledJobStatus) {
            updateScheduledJobs(input: {id: $id, scheduledJobStatus: $scheduledJobStatus}) {
                id
            }
        }
    """
    params = {"id": job_id, "scheduledJobStatus": "PENDING"}
    return call_graphql(query=query, params=params, message="mark_my_job_as_pending")


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


def get_schedules_near_time(params: dict):
    query = """
        query MyQuery($scheduledJobStatus: ScheduledJobStatus!, $ge: String, $le: String, $nextToken: String, $limit: Int = 1000) {
            scheduledJobsByStatusAndTime(scheduledJobStatus: $scheduledJobStatus, filter: {isDeleted: {ne: true}}, limit: $limit, scheduledJobTime: {ge: $ge, le: $le}, nextToken: $nextToken) {
                nextToken
                items {
                    id
                    user_requested
                    requestMeta
                    scheduledJobStatus
                    scheduledJobTime
                    scheduledJobType
                }
            }
        }
    """

    return call_graphql(query=query, params=params, message="get_schedules_near_time")
