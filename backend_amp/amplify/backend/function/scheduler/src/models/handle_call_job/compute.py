import requests
from requests import Response
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
        self.collection = get_schedules_collection()

    def execute_job(self) -> Response:
        url = self.url + '/actions/call'
        payload = {
            'type_': 'scheduled',
            'scheduledId': str(self.job._id),
            'user_id': str(self.job.user_id),
            'expert_id': str(self.job.expert_id),
            'user_requested': self.job.user_requested
        }

        response = requests.post(url, json=payload)
        print(response.text)

        return response

    def compute(self) -> Response:
        response = self.execute_job()
        response = response.json()
        response = Output(**response)
        status = response.output_message
        if response.output_status == OutputStatus.FAILURE:
            # TODO: Send slack message
            pass
        self.common.update_schedule_status(self.job._id, status)

        return Output(output_message="Job executed successfully")
