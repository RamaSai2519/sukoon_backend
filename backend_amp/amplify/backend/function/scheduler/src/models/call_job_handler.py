import requests
import json
from models.iprocessor import IProcessor
from queries.scheduled_job import update_scheduled_job_status


class CallJobHandler(IProcessor):
    def __init__(self, job):
        self.job_id = job.get('id', '')
        self.user_requested = job.get('user_requested', None)
        self.request_meta = json.loads(job.get('requestMeta')) or {}

    def invoke_call_backend_api(self):
        url = 'https://6x4j0qxbmk.execute-api.ap-south-1.amazonaws.com/main/actions/call'

        headers = {'Content-Type': 'application/json'}

        payload = json.dumps({
            'type_': 'scheduled',
            'scheduledId': self.job_id,
            'user_requested': self.user_requested,
            'user_id': self.request_meta.get('userId'),
            'expert_id': self.request_meta.get('expertId'),
        })

        response = requests.request('POST', url, headers=headers, data=payload)
        print(response.text)

        return response

    def process_scheduled_job(self):
        response = self.invoke_call_backend_api()
        json_response = response.json()
        status = json_response.get('output_message')
        update_scheduled_job_status(self.job_id, status)

        return response
