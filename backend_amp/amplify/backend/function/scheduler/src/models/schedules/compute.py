from shared.models.interfaces import Output, Schedule, WASchedule, WhtasappMessageInput
from shared.db.schedules import get_schedules_collection
from models.handle_call_job.main import CallJobHandler
from models.handle_call_job.wa_notify import WAHandler
from shared.db.experts import get_experts_collections
from models.handle_wa_job.main import WAJobHandler
from shared.configs import CONFIG as config
from shared.models.common import Common
from datetime import timedelta
from typing import Union


class Compute:
    def __init__(self) -> None:
        self.url = config.URL
        self.common = Common()
        self.collection = get_schedules_collection()
        self.now_time = Common.get_current_utc_time()
        self.experts_collection = get_experts_collections()

    def get_lower_time_str(self) -> tuple:
        upper_bound = self.now_time + timedelta(minutes=15)
        lower_bound = upper_bound - timedelta(minutes=5)

        return upper_bound, lower_bound

    def get_wapending_schedules(self) -> list:
        upper_bound, lower_bound = self.get_lower_time_str()
        query = {
            "isDeleted": False,
            "status": "WAPENDING",
            "job_time": {"$gte": lower_bound, "$lt": upper_bound}
        }

        schedules = self.collection.find(query)
        return list(schedules)

    def get_pending_schedules(self) -> list:
        query = {
            "isDeleted": False,
            "job_time": {"$lt": self.now_time},
            "status": "PENDING"
        }

        schedules = self.collection.find(query)
        return list(schedules)

    def execute_jobs(self, job: Union[WASchedule, Schedule]) -> Output:
        if job.job_type == "CALL":
            if job.status == "PENDING":
                handler = CallJobHandler(job)
                output = handler.process()
                return output
            elif job.status == "WAPENDING":
                handler = WAHandler(job)
                output = handler.process()
                return output
        elif job.job_type == "WA":
            if job.status == "PENDING":
                handler = WAJobHandler(job)
                output = handler.process()
                return output

    def compute(self) -> Output:
        p_schedules = self.get_pending_schedules()
        wp_schedules = self.get_wapending_schedules()
        schedules = p_schedules + wp_schedules
        jobs_executed = 0

        for job in schedules:
            if job['job_type'] == "CALL":
                job = Common.clean_dict(job, Schedule)
                job = Schedule(**job)
            elif job['job_type'] == "WA":
                job = Common.clean_dict(job, WASchedule)
                payload = job['payload']
                payload = Common.clean_dict(payload, WhtasappMessageInput)
                job['payload'] = WhtasappMessageInput(**payload)
                job = WASchedule(**job)

            print(f"Executing Job: {job._id}")
            print(f"Current Time: {self.now_time}")
            print(f"Job Time: {job.job_time}")

            self.execute_jobs(job)
            jobs_executed += 1

        if jobs_executed > 0:
            return Output(output_message=f"{jobs_executed} job(s) executed successfully")

        return Output(
            output_status="FAILURE",
            output_message="No jobs executed as it is not the correct day or they were already triggered"
        )
