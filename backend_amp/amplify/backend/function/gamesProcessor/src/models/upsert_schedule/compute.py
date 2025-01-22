import pytz
import requests
from bson import ObjectId
from shared.models.common import Common
from datetime import datetime, timedelta
from shared.configs import CONFIG as config
from shared.db.users import get_user_collection
from shared.db.experts import get_experts_collections
from shared.db.schedules import get_schedules_collection
from shared.models.constants import TimeFormats, OutputStatus
from shared.models.interfaces import UpsertScheduleInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.users_collection = get_user_collection()
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
        time_window = 15 * 60
        start_time = job_time - timedelta(seconds=time_window)
        end_time = job_time + timedelta(seconds=time_window)

        query = {
            "expert_id": expert_id,
            "isDeleted": {"$ne": True},
            "job_time": {"$gte": start_time, "$lte": end_time}
        }
        conflict = self.schedules_collection.find_one(query)
        return conflict is not None

    def check_user_availability(self, user_id: ObjectId, job_time: datetime) -> bool:
        time_window = 15 * 60
        start_time = job_time - timedelta(seconds=time_window)
        end_time = job_time + timedelta(seconds=time_window)

        query = {
            "user_id": user_id,
            "isDeleted": {"$ne": True},
            "job_time": {"$gte": start_time, "$lte": end_time}
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

    def notify_expert(self, url: str, user: dict, expert: dict, difference: int):
        birth_date: datetime = user.get("birthDate", None)
        birth_date = birth_date.strftime(
            "%d %B, %Y") if birth_date else "Not provided"
        payload = {
            "template_name": "SARATHI_NOTIFICATION_FOR_USER_CALL_PRODUCTION",
            "parameters": {
                "last_expert": self.common.get_last_expert_name(self.input.user_id),
                "user_name": user.get("name", "Not provided"),
                "city": user.get("city", "Not provided"),
                "birth_date": birth_date,
                "minutes": int(difference / 60)
            }
        }
        payload['phone_number'] = expert["phoneNumber"]
        response = requests.post(url, json=payload)
        print(response.text, '__expert_immediate_schedule_notification__')

    def notify_user(self, url: str, user: dict, expert: dict, difference: int):
        user_name = user.get('name') or user['phoneNumber']
        expert_name = expert.get('name') or expert['phoneNumber']
        payload = {
            'template_name': 'SCHEDULE_REMINDER_MINUTE_PROD',
            'phone_number': user['phoneNumber'],
            'parameters': {
                'user_name': user_name,
                'expert_name': expert_name,
                'minutes': int(difference / 60)
            }
        }
        response = requests.post(url, json=payload)
        print(response.text, '__user_immediate_schedule_notification__')

    def notify_parties(self, difference: int):
        url = config.URL + '/actions/send_whatsapp'
        user, expert = self.get_parties()
        self.notify_expert(url, user, expert, difference)
        self.notify_user(url, user, expert, difference)

    def compute(self) -> Output:
        if self.input.expert_id:
            expert_id = ObjectId(self.input.expert_id)

            job_time = datetime.strptime(
                self.input.job_time, TimeFormats.AWS_TIME_FORMAT)
            job_time = job_time.replace(tzinfo=pytz.utc)
            difference_seconds = (
                job_time - Common.get_current_utc_time()).total_seconds()
            if difference_seconds < (15 * 60):
                self.notify_parties(difference_seconds)

            if self.check_expert_availability(expert_id, job_time):
                return Output(
                    output_status=OutputStatus.FAILURE,
                    output_message="Expert is not available at this time"
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
