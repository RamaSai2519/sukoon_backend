import json
import time
import requests
from bson import ObjectId
from datetime import datetime
from configs import CONFIG as config
from helpers.slack import SlackNotifier
from models.constants import OutputStatus
from db.users import get_user_collection
from db.calls import get_calls_collection
from db.experts import get_experts_collections
from models.interfaces import CallInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.url = config.URL
        self.call_link = "https://admin.sukoonunlimited.com/admin/calls/"
        self.notifier = SlackNotifier()
        self.users_collection = get_user_collection()
        self.calls_collection = get_calls_collection()
        self.experts_collection = get_experts_collections()

    def get_users(self, user_id: ObjectId, expert_id: ObjectId) -> tuple:
        user = self.users_collection.find_one({"_id": user_id})
        expert = self.experts_collection.find_one({"_id": expert_id})

        return user, expert

    def _make_call(self, user_number: str, expert_number: str):
        knowlarity_url = "https://kpi.knowlarity.com/Basic/v1/account/call/makecall"
        headers = {
            "x-api-key": "bb2S4y2cTvaBVswheid7W557PUzUVMnLaPnvyCxI",
            "authorization": "0738be9e-1fe5-4a8b-8923-0fe503e87deb"
        }
        payload = {
            "k_number": "+918035752993",
            "agent_number": "+91" + expert_number,
            "customer_number": "+91" + user_number,
            "caller_id": "+918035752993"
        }
        response = requests.post(knowlarity_url, headers=headers, json=payload)

        if response.status_code != 200:
            print(response.json(), "Failed to make call")
            return False

        response_dict: dict = response.json()
        success: dict = response_dict.get("success", {})
        call_id = success.get("call_id", None)
        return call_id

    def _update_db(self, user_id: ObjectId, expert_id: ObjectId, call_id: str) -> bool:
        user_update = self.users_collection.update_one(
            {"_id": user_id}, {"$set": {"isBusy": True}})
        if user_update.modified_count == 0:
            print("Failed to update user")
            return False

        expert_update = self.experts_collection.update_one(
            {"_id": expert_id}, {"$set": {"isBusy": True}})
        if expert_update.modified_count == 0:
            print("Failed to update expert")
            return False

        call_insert = self.calls_collection.insert_one(
            {"user": user_id, "expert": expert_id, "callId": call_id, "initiatedTime": datetime.now()})
        if call_insert.inserted_id is None:
            print("Failed to insert call")
            return False

        return True

    def send_fcm_notification(self, user: dict, expert: dict):
        url = self.url + "/actions/push"

        payload = json.dumps({
            "body": "Calling you in a while",
            "title": f"☎️ {user.get('name', '')}",
            "token": expert.get("fcmToken", ""),
            "type_": self.input.type_,
            "user_id": str(user.get("_id", "")),
            "image_url": "https://sukoonunlimited.com/_next/image?url=%2Fplay.jpg&w=3840&q=75",
            "sarathi_id": str(expert.get("_id", ""))
        })
        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response_dict: dict = response.json()
        return response_dict.get("output_message", "")

    def compute(self) -> Output:
        user_id = ObjectId(self.input.user_id)
        expert_id = ObjectId(self.input.expert_id)

        user, expert = self.get_users(user_id, expert_id)
        fcm_response = self.send_fcm_notification(user, expert)

        time.sleep(15)

        call_id = self._make_call(user["phoneNumber"], expert["phoneNumber"])
        if not call_id:
            self.notifier.send_notification(
                type_=self.input.type_,
                user_name=user.get("name", ""),
                sarathi_name=expert.get("name", ""),
                status="error"
            )
            return Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message="Failed to make call"
            )

        db_update = self._update_db(user_id, expert_id, call_id)
        message = "but Failed to update database"
        if db_update:
            message = "and Updated database successfully"
            self.notifier.send_notification(
                type_=self.input.type_,
                user_name=user.get("name", ""),
                sarathi_name=expert.get("name", ""),
                status="success",
                call_link=self.call_link + call_id,
            )


        return Output(
            output_details={},
            output_status=OutputStatus.SUCCESS,
            output_message="Call initiated with callid: " + call_id + message + fcm_response
        )
