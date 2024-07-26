import requests
import json
from models.iprocessor import IProcessor

class CallJobHandler(IProcessor):
    def __init__(self, job):
        self.request_meta = json.loads(job.get("requestMeta")) or {}

    def invoke_call_backend_api(self):
        url = "https://prod-backend.sukoonunlimited.com/api/call/backend-make-call"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9',
        }

        payload = json.dumps({
            "userId": self.request_meta.get("userId"),
            "expertId": self.request_meta.get("expertId"),
            "scheduledCallId": self.request_meta.get("scheduledCallId", "") or "",
        })

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)

        return response.text


    def process_scheduled_job(self):
        response = self.invoke_call_backend_api()

        return response

