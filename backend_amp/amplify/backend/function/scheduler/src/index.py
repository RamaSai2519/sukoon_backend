import json
import controller
from models.wa_notify import WAHandler
from shared.models.common import Common
from datetime import datetime, timedelta
from shared.models.constants import TimeFormats
from models.experts_status_job.main import StatusJob
from queries.scheduled_job import get_pending_scheduled_jobs, mark_my_job_as_picked, get_schedules_near_time


def construct_response(statusCode, body):
    response = {
        "statusCode": statusCode,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
        "body": json.dumps(body),
    }
    return response


job_error = "error in executing processor for job {job} with error {error}"
fetch_error = "error in getting scheduled job for time {time} and status {status} error {error}"


def get_lower_time_str(time_str: str) -> tuple:
    time_format = TimeFormats.AWS_TIME_FORMAT
    input_time = datetime.strptime(time_str, time_format)

    upper_bound = input_time + timedelta(minutes=30)
    lower_bound = upper_bound - timedelta(minutes=5)

    lower_bound_str = lower_bound.strftime(time_format)
    upper_bound_str = upper_bound.strftime(time_format)

    return upper_bound_str, lower_bound_str


def handle_wa_notifications(time_str: str) -> None:
    next_token = None
    status = "WAPENDING"
    upper_bound_str, lower_bound_str = get_lower_time_str(time_str)
    params = {"scheduledJobStatus": status, "ge": lower_bound_str, "le": upper_bound_str,
              "nextToken": next_token, "limit": 1000}
    all_jobs = []
    hit = 0

    while True:
        if next_token:
            params['nextToken'] = next_token
        else:
            params.pop('nextToken', None)

        response = get_schedules_near_time(params)
        hit += 1
        print(f"{hit}Response: {response}")
        all_jobs.extend(response['scheduledJobsByStatusAndTime']['items'])

        next_token = response['scheduledJobsByStatusAndTime'].get('nextToken')
        if not next_token:
            break

    for job in all_jobs:
        wa_handler = WAHandler(job)
        wa_handler.reminder_user()


def handle_other_jobs(time: str) -> None:
    # Experts Status Update
    status_job = StatusJob()
    output = status_job.process()
    print(f"Status Job Output: {output}\n")

    # WA Notifications
    handle_wa_notifications(time)

    return "Jobs Handled"


def handler(event, context):
    try:
        print(f"Event: {event}")
        print(f"Context: {context} \n")

        time = event["time"]
        status = "PENDING"

        output = handle_other_jobs(time)
        print(output)

        next_token = None
        first_time = True

        while next_token or first_time:
            data = get_pending_scheduled_jobs(
                status=status, time=time, next_token=next_token
            )["scheduledJobsByStatusAndTime"]

            jobs = data["items"]
            print(jobs)
            for job in jobs:
                try:
                    if job.get("scheduledJobType"):
                        controller.process(job)
                    else:
                        print(f"no job type for given job {job}")
                except Exception as error:
                    error = job_error.format(job=job, error=error)
                    print(error)
                if job.get("id"):
                    mark_my_job_as_picked(job.get("id", None))
            first_time = False
            next_token = data["nextToken"]

    except Exception as error:
        error = fetch_error.format(time=time, status=status, error=error)
        print(error)
        return construct_response(statusCode=400, body={})
    return construct_response(statusCode=200, body={})


if __name__ == "__main__":
    common = Common()
    time = common.current_time
    time_str = time.strftime(TimeFormats.AWS_TIME_FORMAT)
    handler({"time": time_str}, None)
