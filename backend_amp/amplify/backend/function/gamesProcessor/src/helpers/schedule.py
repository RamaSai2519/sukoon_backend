import json
import requests
from datetime import datetime


class ScheduleManager:
    @staticmethod
    def scheduleCall(time: datetime, expert_id: str, user_id: str, recordId: str) -> str:
        url = "https://6x4j0qxbmk.execute-api.ap-south-1.amazonaws.com/main/actions/create_scheduled_job"
        time = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        meta = {"expertId": expert_id,
                "userId": user_id, "scheduledCallId": recordId}
        meta = json.dumps(meta)
        payload = {
            "job_type": "CALL",
            "job_time": time,
            "status": "PENDING",
            "request_meta": meta,
        }
        response = requests.request("POST", url, data=json.dumps(payload))
        return response.text

    @staticmethod
    def cancelCall(scheduleId: str) -> str:
        url = "https://6x4j0qxbmk.execute-api.ap-south-1.amazonaws.com/main/actions/update_scheduled_job"
        payload = {
            "action": "DELETE",
            "scheduled_job_id": scheduleId
        }
        response = requests.request("POST", url, data=json.dumps(payload))
        return response.text
