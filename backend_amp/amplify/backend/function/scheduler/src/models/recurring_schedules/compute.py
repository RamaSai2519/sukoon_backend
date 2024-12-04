from shared.db.schedules import get_reschedules_collection
from shared.db.experts import get_experts_collections
from shared.configs import CONFIG as config
from shared.models.interfaces import Output
from datetime import datetime
from bson import ObjectId


class Compute:
    def __init__(self) -> None:
        self.url = config.URL
        self.now_time = datetime.now()
        self.collection = get_reschedules_collection()
        self.experts_collection = get_experts_collections()
        self.now_day = self.now_time.strftime("%A").lower()
        self.is_even_week = self.current_week_number % 2 == 0
        self.current_week_number = (self.now_time.day - 1) // 7 + 1

    def get_reschedules(self) -> list:
        query = {
            "job_expiry": {"$gte": self.now_time},
            "days": self.now_day,
        }
        reschedules = self.collection.find(query)
        return list(reschedules)

    def has_been_triggered_today(self, job) -> bool:
        last_triggered = job.get("last_triggered")
        if not last_triggered:
            return False

        last_triggered_date = datetime.strptime(
            last_triggered, "%Y-%m-%d").date()
        return last_triggered_date == self.now_time.date()

    def mark_as_triggered(self, job_id: ObjectId):
        self.collection.update_one(
            {"_id": job_id},
            {"$set": {"last_triggered": self.now_time.strftime("%Y-%m-%d")}}
        )

    def execute_job(self, job):
        pass

    def compute(self) -> Output:
        reschedules = self.get_reschedules()
        jobs_executed = 0

        for job in reschedules:
            if self.has_been_triggered_today(job):
                continue

            frequency = job["frequency"].lower()
            month_days = job.get("month_days", [])
            month_weeks = job.get("month_weeks", "").lower()

            if frequency == "weekly":
                if month_weeks == "even" and not self.is_even_week:
                    continue
                if month_weeks == "odd" and self.is_even_week:
                    continue
                if self.now_day in job["days"]:
                    self.execute_job(job)
                    self.mark_as_triggered(job["_id"])
                    jobs_executed += 1

            elif frequency == "monthly":
                if self.now_time.day in month_days:
                    self.execute_job(job)
                    self.mark_as_triggered(job["_id"])
                    jobs_executed += 1

        if jobs_executed > 0:
            return Output(
                output_status="SUCCESS",
                output_message=f"{jobs_executed} job(s) executed successfully"
            )
        return Output(
            output_status="FAILURE",
            output_message="No jobs executed as it is not the correct day or they were already triggered"
        )
