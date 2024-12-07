from shared.models.interfaces import Output, RecurringSchedule
from shared.db.schedules import get_reschedules_collection
from shared.db.experts import get_experts_collections
from shared.models.constants import TimeFormats
from shared.configs import CONFIG as config
from datetime import datetime, timedelta
from shared.models.common import Common
from bson import ObjectId
import requests


class Compute:
    def __init__(self, time: str) -> None:
        self.now_time = datetime.strptime(time, TimeFormats.AWS_TIME_FORMAT)
        self.now_week_day = self.get_week_day()
        self.now_month_day = self.get_month_day()
        self.url = config.URL + '/actions/schedules'
        self.collection = get_reschedules_collection()
        self.experts_collection = get_experts_collections()

    def get_week_day(self) -> str:
        time = self.now_time + timedelta(hours=5, minutes=30)
        return time.strftime('%A').lower()

    def get_month_day(self) -> int:
        time = self.now_time + timedelta(hours=5, minutes=30)
        return time.day

    def get_reschedules(self) -> list:
        last_triggered_lt = {'$lt': self.now_time.replace(
            hour=0, minute=0, second=0, microsecond=0)}
        last_triggered_ex = {'$exists': False}
        job_expiry_gt = {'$gt': self.now_time}
        query = {
            '$and': [
                {'job_expiry': job_expiry_gt},
                {'$or': [
                    {'last_triggered': last_triggered_lt},
                    {'last_triggered': last_triggered_ex}
                ]}
            ]
        }

        reschedules = self.collection.find(query)
        return list(reschedules)

    def mark_as_triggered(self, job_id: ObjectId):
        self.collection.update_one(
            {'_id': job_id},
            {'$set': {'last_triggered': self.now_time}}
        )
        pass

    def execute_job(self, job: RecurringSchedule):
        job_hour = int(job.job_time.split(':')[0])
        job_minute = int(job.job_time.split(':')[1])

        time = self.now_time.replace(
            hour=job_hour, minute=job_minute, day=self.now_time.day + 1)
        time = time - timedelta(hours=5, minutes=30)
        status = 'PENDING'
        print(f"Job time: {time}, Current time: {self.now_time}")
        if self.now_time > time:
            print(f"Skipping job {job._id} as it is too late to schedule")
            return

        if job.job_type == 'CALL':
            status = 'WAPENDING'
            if (time - self.now_time).total_seconds() < 30 * 60:
                status = 'PENDING'
                print(
                    f"Job {job._id} is too close to schedule, setting status to PENDING")

        payload = {
            'status': status,
            'initiatedBy': job.name,
            'job_type': job.job_type,
            'user_id': str(job.user_id),
            'reschedule_id': str(job._id),
            'expert_id': str(job.expert_id),
            'user_requested': job.user_requested,
            'job_time': time.strftime(TimeFormats.AWS_TIME_FORMAT)
        }
        response = requests.post(self.url, json=payload)
        response = response.json()
        response = Output(**response)
        print(response.output_message)

    def compute(self) -> Output:
        reschedules = self.get_reschedules()
        jobs_executed = 0

        for job in reschedules:
            job = Common.clean_dict(job, RecurringSchedule)
            job = RecurringSchedule(**job)

            print(f"Checking job {str(job._id)}")
            print(f"Job frequency: {job.frequency}\n\n")
            if job.frequency == 'daily':
                self.execute_job(job)
                jobs_executed += 1
                self.mark_as_triggered(job._id)
            elif job.frequency == 'weekly':
                print(f"Job week days: {job.week_days}")
                print(f"Current week day: {self.now_week_day}\n\n")
                if self.now_week_day in job.week_days:
                    self.execute_job(job)
                    jobs_executed += 1
                    self.mark_as_triggered(job._id)
            elif job.frequency == 'monthly':
                print(f"Job month days: {job.month_days}")
                print(f"Current month day: {self.now_month_day}\n\n")
                if self.now_month_day in job.month_days:
                    self.execute_job(job)
                    jobs_executed += 1
                    self.mark_as_triggered(job._id)
            else:
                continue

        if jobs_executed > 0:
            return Output(output_message=f'{jobs_executed} job(s) executed successfully')
        return Output(
            output_status='FAILURE',
            output_message='No jobs executed as it is not the correct day or they were already triggered'
        )
