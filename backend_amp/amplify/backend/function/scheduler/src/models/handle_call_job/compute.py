import requests
from requests import Response
from .slack import SlackManager
from shared.models.common import Common
from shared.configs import CONFIG as config
from shared.models.constants import OutputStatus
from shared.models.interfaces import Schedule, Output
from shared.db.schedules import get_schedules_collection


class Compute:
    def __init__(self, input: Schedule) -> None:
        self.job = input
        self.url = config.URL
        self.common = Common()
        self.slack = SlackManager()
        self.collection = get_schedules_collection()

    def execute_job(self) -> Response:
        url = self.url + '/actions/call'
        payload = {
            'wait': False,
            'type_': 'scheduled',
            'scheduledId': str(self.job._id),
            'user_id': str(self.job.user_id),
            'expert_id': str(self.job.expert_id),
            'user_requested': self.job.user_requested,
        }

        balance = self.common.get_balance_type(str(self.job.expert_id))
        token = Common.get_token(str(self.job.user_id), balance)
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.post(url, json=payload, headers=headers)
        print(response.text)

        return response

    def compute(self) -> Response:
        response = self.execute_job()
        response = response.json()
        response = Output(**response)
        status = response.output_message
        if response.output_status == OutputStatus.FAILURE:
            message = self.slack.send_message(
                self.job.user_id, self.job.expert_id, status)
            print(message)
        self.common.update_schedule_status(self.job._id, status)

        return Output(output_message="Job executed successfully")
