import json
import requests
from typing import Tuple
from bson import ObjectId
from shared.models.common import Common
from shared.configs import CONFIG as config
from shared.helpers.users import UsersHelper
from shared.helpers.experts import ExpertsHelper
from shared.models.interfaces import User, Expert
from queries.scheduled_job import mark_my_job_as_pending


class WAHandler:
    def __init__(self, job: dict) -> None:
        self.url = config.URL
        self.common = Common()
        self.job_id = job.get('id', '')
        self.users_helper = UsersHelper()
        self.experts_helper = ExpertsHelper()
        self.request_meta = json.loads(job.get('requestMeta')) or {}

    def get_participants(self) -> Tuple[User, Expert]:
        userId = self.request_meta.get('userId')
        expertId = self.request_meta.get('expertId')

        user = self.users_helper.get_user(user_id=userId)
        expert = self.experts_helper.get_expert(expert_id=expertId)

        return user, expert

    def invoke_whatsapp_api(self) -> requests.Response:
        url = self.url + '/actions/send_whatsapp'
        headers = {'Content-Type': 'application/json'}
        user, expert = self.get_participants()
        user_name = user.name or user.phoneNumber
        expert_name = expert.name or expert.phoneNumber
        names = {
            'user_name': user_name,
            'expert_name': expert_name
        }

        payload = json.dumps({
            'template_name': 'SCHEDULE_REMINDER',
            'phone_number': user.phoneNumber,
            'request_meta': json.dumps(names),
            'parameters': names
        })

        response = requests.request('POST', url, headers=headers, data=payload)
        print(response.text)

        return response

    def reminder_user(self) -> requests.Response:
        try:
            response = self.invoke_whatsapp_api()
        except Exception as error:
            print(f"error in executing wa notification for job {self.job_id} with error {error}")
            response = None
        mark_my_job_as_pending(self.job_id)

        return response
