from shared.models.constants import application_json_header
from shared.models.interfaces import CallInput as Input
from shared.configs import CONFIG as config
from shared.models.common import Common
from datetime import datetime
import requests
import json


class Notifications:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.url = config.URL
        self.common = Common()

    def send_fcm_notification(self, user: dict, expert: dict):
        url = self.url + "/actions/push"

        payload = json.dumps({
            "body": "Calling you in a while",
            "title": f"☎️ {user.get('name', '')}",
            "token": expert.get("fcmToken", ""),
            "type_": self.input.type_,
            "sound": "longbell",
            "priority": "high",
            "user_id": str(user.get("_id", "")),
            "image_url": "https://sukoonunlimited.com/_next/image?url=%2Fplay.jpg&w=3840&q=75",
            "sarathi_id": str(expert.get("_id", ""))
        })

        response = requests.request(
            "POST", url, headers=application_json_header, data=payload)
        response_dict: dict = response.json()
        response_str: str = response_dict.get("output_message", "")
        return " and " + response_str

    def send_wa_notification(self, user: dict, expert: dict) -> str:
        url = self.url + "/actions/send_whatsapp"
        birth_date: datetime = user.get("birthDate", None)
        if birth_date and not isinstance(birth_date, str):
            birth_date = birth_date.strftime(
                "%d %B, %Y")
        else:
            birth_date = "Not provided"

        payload = json.dumps({
            "phone_number": expert.get("phoneNumber", ""),
            "template_name": "CALL_NOTIFICATION",
            "parameters": {
                "last_expert": self.common.get_last_expert_name(self.input.user_id),
                "user_name": user.get("name", "Not provided"),
                "city": user.get("city", "Not provided"),
                "birth_date": birth_date,
                "premium": 'Unavailable'
            },
            'skip_check': True
        })

        response = requests.request(
            "POST", url, headers=application_json_header, data=payload)
        response_dict: dict = response.json()
        response_str = response_dict.get("output_message", "")
        return " and " + response_str
