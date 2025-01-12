import json
import pytz
import requests
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

    def invoke_whatsapp_api(self) -> requests.Response:
        url = self.url + '/actions/send_whatsapp'
        user, expert = self.get_participants()
        user_name = user.name or user.phoneNumber
        expert_name = expert.name or expert.phoneNumber
        job_time = datetime.strptime(
            self.job.job_time, TimeFormats.AWS_TIME_FORMAT)
        job_time = job_time.replace(tzinfo=pytz.utc)
        difference_seconds = (
                job_time - Common.get_current_utc_time()).total_seconds()
        payload = {
            'template_name': 'SCHEDULE_REMINDER_MINUTE_PROD',
            'phone_number': user.phoneNumber,
            'parameters': {
                'expert_name': user_name,
                'user_name': expert_name,
                'minutes': int(difference_seconds / 60)
            }
        }
        response = requests.post(url, json=payload)
        print(response.text)

        return response.text

    def process(self) -> Output:
        try:
            response = self.invoke_whatsapp_api()
        except Exception as error:
            print(error, "Error in sending whatsapp message: {job}".format(
                job=self.job.__dict__))
            response = None
        self.common.update_schedule_status(self.job._id, "PENDING")

        return Output(output_details=response)
