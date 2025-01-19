import pytz
import requests
import traceback
from typing import Tuple
from datetime import datetime
from shared.models.common import Common
from shared.configs import CONFIG as config
from shared.helpers.users import UsersHelper
from shared.models.constants import TimeFormats
from shared.helpers.experts import ExpertsHelper
from shared.db.schedules import get_schedules_collection
from shared.models.interfaces import User, Expert, Schedule, Output


class WAHandler:
    def __init__(self, job: Schedule) -> None:
        self.job = job
        self.url = config.URL
        self.common = Common()
        self.users_helper = UsersHelper()
        self.experts_helper = ExpertsHelper()
        self.collection = get_schedules_collection()

    def get_participants(self) -> Tuple[User, Expert]:
        user_id = self.job.user_id
        expert_id = self.job.expert_id

        user = self.users_helper.get_user(user_id=user_id)
        user = Common.clean_dict(user, User)
        user = User(**user)

        expert = self.experts_helper.get_expert(expert_id=expert_id)
        expert = Common.clean_dict(expert, Expert)
        expert = Expert(**expert)

        return user, expert

    def get_diff_in_minutes(self, difference_in_seconds: int) -> str:
        minutes = int(difference_in_seconds / 60)
        if minutes <= 2:
            return 'couple of'
        return str(minutes)

    def notify_user(self, phoneNumber: str, user_name: str, expert_name: str, difference: str) -> str:
        url = self.url + '/actions/send_whatsapp'
        payload = {
            'template_name': 'SCHEDULE_REMINDER_MINUTE_PROD',
            'phone_number': phoneNumber,
            'parameters': {
                'expert_name': user_name,
                'user_name': expert_name,
                'minutes': difference
            }
        }
        response = requests.post(url, json=payload)
        print(response.text, '__user_scheduler_notification__')

        return response.text

    def notify_expert(self, phoneNumber: str, user_name: str, user_city: str, user_birth: str, difference: str) -> str:
        url = self.url + '/actions/send_whatsapp'
        payload = {
            'template_name': 'SARATHI_NOTIFICATION_FOR_USER_CALL_PRODUCTION',
            'phone_number': phoneNumber,
            'parameters': {
                "last_expert": self.common.get_last_expert_name(str(self.job.user_id)),
                "user_name": user_name,
                "city": user_city,
                "birth_date": user_birth,
                "minutes": difference
            }
        }
        response = requests.post(url, json=payload)
        print(response.text, '__expert_scheduler_notification__')

        return response.text

    def process(self) -> Output:
        user, expert = self.get_participants()
        user_name = user.name or user.phoneNumber
        expert_name = expert.name or expert.phoneNumber
        job_time: datetime = self.job.job_time.replace(tzinfo=pytz.utc)
        difference_seconds = (
            job_time - Common.get_current_utc_time()).total_seconds()
        birth_date = user.birthDate
        if isinstance(birth_date, str):
            birth_date = datetime.strptime(
                birth_date, TimeFormats.ANTD_TIME_FORMAT)
        birth_date = birth_date.strftime(
            "%d %B, %Y") if birth_date else "Not provided"
        try:
            difference_minutes = self.get_diff_in_minutes(difference_seconds)
            user_response = self.notify_user(
                user.phoneNumber, user_name, expert_name, difference_minutes)
            expert_response = self.notify_expert(
                expert.phoneNumber, user_name, user.city, birth_date, difference_minutes)
        except Exception as error:
            traceback.print_exc()
            print(error, "Error in sending whatsapp message: {job}".format(
                job=self.job.__dict__))
            user_response = None
            expert_response = None
        self.common.update_schedule_status(self.job._id, "PENDING")

        return Output(
            output_message=f"User: {user_response}, Expert: {expert_response}"
        )
