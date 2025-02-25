import pytz
import requests
from bson import ObjectId
from .slack import SlackManager
from shared.models.common import Common
from datetime import datetime, timedelta
from shared.db.users import get_user_collection
from shared.db.schedules import get_schedules_collection
from shared.models.constants import TimeFormats, OutputStatus
from shared.models.interfaces import UpsertScheduleInput as Input, Output
from shared.db.experts import get_experts_collections, get_timings_collection


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.users_collection = get_user_collection()
        self.timings_collection = get_timings_collection()
        self.experts_collection = get_experts_collections()
        self.schedules_collection = get_schedules_collection()

    def prep_data(self, new_data: dict, old_data: dict = None) -> dict:
        if self.input.isDeleted:
            return {"_id": ObjectId(self.input._id), "isDeleted": True}

        new_data.pop('_id', None)
        if old_data:
            mutable_fields = ['job_time', 'job_type', 'status',
                              'user_requested', 'reschedule_id']
            for field, value in old_data.items():
                if field in mutable_fields:
                    new_data[field] = value

        object_fields = ['user_id', 'expert_id']
        for field in object_fields:
            if isinstance(new_data.get(field), str):
                new_data[field] = ObjectId(new_data[field])

        if isinstance(new_data.get('job_time'), str):
            new_data['job_time'] = datetime.strptime(
                new_data['job_time'], TimeFormats.AWS_TIME_FORMAT)

        new_data = Common.filter_none_values(new_data)
        return new_data

    def get_old_data(self) -> dict:
        query = {"_id": ObjectId(self.input._id)}
        old_data = self.schedules_collection.find_one(query)
        return old_data

    def check_expert_availability(self, expert_id: ObjectId, job_time: datetime) -> bool:
        if self._has_schedule_conflict(expert_id, job_time) or not self._is_expert_available(expert_id, job_time):
            return True
        return False

    def _has_schedule_conflict(self, expert_id: ObjectId, job_time: datetime) -> bool:
        time_window = 15 * 60
        start_time = job_time - timedelta(seconds=time_window)
        end_time = job_time + timedelta(seconds=time_window)

        query = {
            "expert_id": expert_id,
            "isDeleted": {"$ne": True},
            "job_time": {"$gte": start_time, "$lte": end_time},
            "status": {"$eq": {"$regex": "pending", "$options": "i"}}
        }
        doc = self.schedules_collection.find_one(query)
        return doc is not None

    def _is_expert_available(self, expert_id: ObjectId, job_time: datetime) -> bool:
        if not self.common.check_vacation(expert_id, job_time):
            return False

        job_time += timedelta(hours=5, minutes=30)
        ctime = job_time.replace(minute=0)
        hour = int(ctime.strftime(TimeFormats.HOURS_24_FORMAT).split(':')[0])
        query = {'expert': expert_id, 'day': job_time.strftime('%A')}
        timing: dict = self.timings_collection.find_one(query)
        if not timing:
            return True

        start_time_one = timing.get('PrimaryStartTime')
        end_time_one = timing.get('PrimaryEndTime')
        start_time_two = timing.get('SecondaryStartTime')
        end_time_two = timing.get('SecondaryEndTime')
        all_fields = [start_time_one, end_time_one,
                      start_time_two, end_time_two]
        if all(field is None for field in all_fields) or all(field == '' for field in all_fields):
            return True
        return self._is_within_timing(hour, start_time_one, end_time_one) or self._is_within_timing(hour, start_time_two, end_time_two)

    def _is_within_timing(self, hour: int, start_time: str, end_time: str) -> bool:
        if start_time and end_time and start_time != '' and end_time != '':
            try:
                start_hour = int(start_time.split(':')[0])
                end_hour = int(end_time.split(':')[0])
            except Exception:
                return False
            return start_hour <= hour < end_hour
        return False

    def check_user_availability(self, user_id: ObjectId, job_time: datetime) -> bool:
        time_window = 15 * 60
        start_time = job_time - timedelta(seconds=time_window)
        end_time = job_time + timedelta(seconds=time_window)

        query = {
            "user_id": user_id,
            "isDeleted": {"$ne": True},
            "job_time": {"$gte": start_time, "$lte": end_time},
            "status": {"$eq": {"$regex": "pending", "$options": "i"}}
        }
        conflict = self.schedules_collection.find_one(query)
        return conflict is not None

    def get_parties(self) -> tuple:
        query = {"_id": ObjectId(self.input.expert_id)}
        projection = {"customerPersona": 0, "persona": 0}
        expert = self.experts_collection.find_one(query, projection)
        query = {"_id": ObjectId(self.input.user_id)}
        user = self.users_collection.find_one(query, projection)
        return user, expert

    def compute(self) -> Output:
        if self.input.expert_id:
            expert_id = ObjectId(self.input.expert_id)

            job_time = datetime.strptime(
                self.input.job_time, TimeFormats.AWS_TIME_FORMAT)
            job_time = job_time.replace(tzinfo=pytz.utc)

            if self.check_expert_availability(expert_id, job_time):
                return Output(
                    output_status=OutputStatus.FAILURE,
                    output_message="Expert is not available at this time, please recheck expert timings and upcoming schedules"
                )

        if self.input.user_id:
            user_id = ObjectId(self.input.user_id)
            job_time = datetime.strptime(
                self.input.job_time, TimeFormats.AWS_TIME_FORMAT)
            job_time = job_time.replace(tzinfo=pytz.utc)
            if self.check_user_availability(user_id, job_time):
                return Output(
                    output_status=OutputStatus.FAILURE,
                    output_message="User is not available at this time"
                )

        if self.input.initiatedBy and self.input.initiatedBy.lower() == 'ark':
            user, expert = self.get_parties()
            user_name = user.get('name') or user['phoneNumber']
            expert_name = expert.get('name') or expert['phoneNumber']
            slack = SlackManager(user_name, expert_name)
            msg = slack.send_message()
            print(msg, '__ark_schedule_slack__')

        if self.input._id:
            old_data = self.get_old_data()
            new_data = self.prep_data(self.input.__dict__, old_data)
            new_data['updated_at'] = datetime.now()
            self.schedules_collection.update_one(
                {"_id": ObjectId(self.input._id)}, {"$set": new_data})
            return Output(
                output_details=Common.jsonify(new_data),
                output_message="Schedule updated successfully"
            )
        else:
            new_data = self.prep_data(self.input.__dict__)
            new_data['created_at'] = datetime.now()
            self.schedules_collection.insert_one(new_data)
            return Output(
                output_details=Common.jsonify(new_data),
                output_message="Schedule created successfully"
            )
