from shared.models.interfaces import Output, RecurringSchedule
from shared.db.schedules import get_reschedules_collection
from shared.db.experts import get_experts_collections
from shared.models.constants import TimeFormats
from shared.configs import CONFIG as config
from shared.models.common import Common
from datetime import datetime
from bson import ObjectId
import requests


class Compute:
    def __init__(self) -> None:
        self.url = config.URL + '/actions/schedules'
        self.now_time = datetime.now()
        self.collection = get_reschedules_collection()
        self.experts_collection = get_experts_collections()
        self.now_day = self.now_time.strftime('%A').lower()

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

    def execute_job(self, job: RecurringSchedule):
        job_time = job.job_time
        time = datetime.strptime(job_time, TimeFormats.HOURS_24_FORMAT)
        time = time.replace(year=self.now_time.year,
                            month=self.now_time.month, day=self.now_time.day)
        status = 'PENDING'
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

            if job.frequency == 'daily':
                self.execute_job(job)
                jobs_executed += 1
                self.mark_as_triggered(job._id)
            elif job.frequency == 'weekly':
                if self.now_day.lower() in job.week_days:
                    self.execute_job(job)
                    jobs_executed += 1
                    self.mark_as_triggered(job._id)
            elif job.frequency == 'monthly':
                if self.now_time.day in job.month_days:
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
