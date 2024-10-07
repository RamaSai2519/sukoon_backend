import requests
import json
from models.iprocessor import IProcessor
from queries.scheduled_job import update_scheduled_job_status


class CallJobHandler(IProcessor):
    def __init__(self, job):
        self.request_meta = json.loads(job.get("requestMeta")) or {}
        self.job_id = job.get("id", "")

    def invoke_call_backend_api(self):
        url = "https://6x4j0qxbmk.execute-api.ap-south-1.amazonaws.com/main/actions/call"

        headers = {'Content-Type': 'application/json'}

        payload = json.dumps({
            "userId": self.request_meta.get("userId"),
            "expertId": self.request_meta.get("expertId"),
            "scheduledCallId": self.request_meta.get("scheduledCallId", "") or "",
        })

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)

        return response

    def process_scheduled_job(self):
        response = self.invoke_call_backend_api()
        json_response = response.json()
        status = json_response.get('output_message')
        update_scheduled_job_status(self.job_id, status)

        return response
