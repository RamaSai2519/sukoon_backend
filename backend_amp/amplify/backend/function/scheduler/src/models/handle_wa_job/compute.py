import requests
from requests import Response
from shared.models.common import Common
from shared.configs import CONFIG as config
from shared.models.interfaces import WASchedule, Output
from shared.db.schedules import get_schedules_collection


class Compute:
    def __init__(self, input: WASchedule) -> None:
        self.job = input
        self.url = config.URL
        self.common = Common()
        self.collection = get_schedules_collection()

    def execute_job(self) -> Response:
        url = self.url + '/actions/send_whatsapp'
        payload = self.job.payload.__dict__
        response = requests.post(url, json=payload)
        print(response.text)

        return response

    def compute(self) -> Response:
        response = self.execute_job()
        response = response.json()
        response = Output(**response)
        status = response.output_message
        self.common.update_schedule_status(self.job._id, status)

        return Output(output_message="Job executed successfully")
