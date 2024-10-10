from models.constants import application_json_header
from models.interfaces import CallInput as Input
from db.calls import get_calls_collection
from configs import CONFIG as config
from models.common import Common
from datetime import datetime
from bson import ObjectId
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
            "priority" :"high",
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
        birth_date: datetime = user.get("birthDate", "")
        if birth_date:
            birth_date = birth_date.strftime("%d %B, %Y")
        premium = "Yes" if user.get("isPaidUser", False) else "No"

        payload = json.dumps({
            "phone_number": expert.get("phoneNumber", ""),
            "template_name": "CALL_NOTIFICATION",
            "parameters": {
                "last_expert": self.get_last_expert_name(),
                "user_name": user.get("name", ""),
                "city": user.get("city", ""),
                "birth_date": birth_date,
                "premium": premium
            }
        })

        response = requests.request(
            "POST", url, headers=application_json_header, data=payload)
        response_dict: dict = response.json()
        response_str = response_dict.get("output_message", "")
        return " and " + response_str

    def get_last_expert_name(self) -> str:
        calls_collection = get_calls_collection()
        query = {"user": ObjectId(self.input.user_id),
                 "status": {"$ne": "initiated"}}
        sort = [("initiatedTime", -1)]
        last_call = dict(calls_collection.find_one(query, sort=sort))
        last_expert = last_call.get("expert", "") if last_call else ""
        last_expert_name = self.common.get_expert_name(last_expert)
        return last_expert_name
