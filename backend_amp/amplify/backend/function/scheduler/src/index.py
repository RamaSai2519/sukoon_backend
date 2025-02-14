import json
from shared.models.common import Common
from models.schedules.main import Schedules
from models.db_backup.main import DbBackupJob
from shared.models.constants import TimeFormats
from models.experts_status_job.main import StatusJob
from models.event_reminder.main import EventReminder
from models.auto_online_job.main import AutoOnlineJob
from models.recurring_schedules.main import RecurringSchedules
from concurrent.futures import ThreadPoolExecutor, as_completed
from models.events_reminders_lister.main import EventsRemindersLister


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

        def schedules_jobs():
            # Recurring Schedules
            reschedules = RecurringSchedules()
            output = reschedules.process(time)
            print(f"Recurring Schedules Output: {output}\n")

            # Schedules
            schedules = Schedules()
            output = schedules.process()
            print(f"Schedules Output: {output}\n")

            return "Schedules Jobs Done"

        def events_reminders_jobs():
            # Events Reminders Lister
            lister = EventsRemindersLister()
            output = lister.process()
            print(f"Events Reminders Lister Output: {output}\n")

            # Event Reminder
            event_reminder = EventReminder()
            output = event_reminder.process()
            print(f"Event Reminder Output: {output}\n")

            return "Events Reminders Jobs Done"

        def experts_jobs():
            # Auto Online Job
            auto_online_job = AutoOnlineJob()
            output = auto_online_job.process()
            print(f"Auto Online Job Output: {output}\n")

            # Experts Status Job
            status_job = StatusJob()
            output = status_job.process()
            print(f"Experts Status Job Output: {output}\n")

            return "Experts Jobs Done"

        def misc_jobs():
            # Db Backup Job
            db_backup_job = DbBackupJob()
            output = db_backup_job.process()
            print(f"Db Backup Job Output: {output}\n")

            return "Misc Jobs Done"

        with ThreadPoolExecutor() as executor:
            methods_to_run = [schedules_jobs, events_reminders_jobs,
                              experts_jobs, misc_jobs]
            futures = {executor.submit(
                method): method for method in methods_to_run}
            for future in as_completed(futures):
                result = future.result()
                print(f"{result}")

    except Exception as error:
        error = fetch_error.format(time=time, status=status, error=error)
        print(error)
        return construct_response(statusCode=400, body={})
    return construct_response(statusCode=200, body={})


if __name__ == "__main__":
    common = Common()
    time = common.get_current_utc_time()
    print(f"Current Time: {time}")
    time_str = time.strftime(TimeFormats.AWS_TIME_FORMAT)
    handler({"time": time_str}, None)
