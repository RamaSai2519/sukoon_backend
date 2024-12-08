import json
from shared.models.common import Common
from models.schedules.main import Schedules
from shared.models.constants import TimeFormats
from models.experts_status_job.main import StatusJob
from models.recurring_schedules.main import RecurringSchedules


def construct_response(statusCode, body) -> dict:
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


def handler(event, context):
    try:
        print(f"Context: {context}")
        time = event["time"]
        print(f"Event Time: {time}")
        status = "PENDING"

        # Experts Status Job
        status_job = StatusJob()
        output = status_job.process()
        print(f"Experts Status Job Output: {output}\n")

        # Recurring Schedules
        reschedules = RecurringSchedules()
        output = reschedules.process(time)
        print(f"Recurring Schedules Output: {output}\n")

        # Schedules
        schedules = Schedules()
        output = schedules.process()
        print(f"Schedules Output: {output}\n")

    except Exception as error:
        error = fetch_error.format(time=time, status=status, error=error)
        print(error)
        return construct_response(statusCode=400, body={})
    return construct_response(statusCode=200, body={})


if __name__ == "__main__":
    common = Common()
    time = common.current_time
    print(f"Current Time: {time}")
    time_str = time.strftime(TimeFormats.AWS_TIME_FORMAT)
    handler({"time": time_str}, None)
