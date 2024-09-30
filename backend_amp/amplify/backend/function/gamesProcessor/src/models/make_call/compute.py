import pytz
import time
import requests
from bson import ObjectId
from datetime import datetime
from dataclasses import asdict
from typing import Tuple, Dict
from db.users import get_user_collection
from db.calls import get_calls_collection
from models.constants import OutputStatus
from db.experts import get_experts_collections
from models.make_call.slack import SlackNotifier
from models.make_call.notifications import Notifications
from models.interfaces import CallInput as Input, Output, Call


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.notifier = Notifications(input)
        self.slack_notifier = SlackNotifier()
        self.users_collection = get_user_collection()
        self.calls_collection = get_calls_collection()
        self.experts_collection = get_experts_collections()
        self.call_link = "https://admin.sukoonunlimited.com/admin/calls/"

    def get_users(self, user_id: ObjectId, expert_id: ObjectId) -> Tuple[Dict, Dict]:
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

    def prep_call(self, user_id: ObjectId, expert_id: ObjectId, call_id: str) -> dict:
        call = Call(user=user_id, expert=expert_id, callId=call_id,
                    initiatedTime=datetime.now(pytz.utc), status="initiated")
        return asdict(call)

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

        call = self.prep_call(user_id, expert_id, call_id)
        call = {k: v for k, v in call.items() if v is not None}
        call_insert = self.calls_collection.insert_one(call)
        if call_insert.inserted_id is None:
            print("Failed to insert call")
            return False

        return True

    def compute(self) -> Output:
        user_id = ObjectId(self.input.user_id)
        expert_id = ObjectId(self.input.expert_id)

        user, expert = self.get_users(user_id, expert_id)
        if not user or not expert:
            return Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message="User or Expert not found"
            )

        fcm_response = self.notifier.send_fcm_notification(user, expert)
        if expert.get("type") != "internal":
            wa_response = self.notifier.send_wa_notification(user, expert)
        else:
            wa_response = " but Expert is internal, no whatsapp notification sent"

        time.sleep(15)

        call_id = self._make_call(user["phoneNumber"], expert["phoneNumber"])
        if not call_id:
            self.slack_notifier.send_notification(
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
        message = " but Failed to update database"
        if db_update:
            message = " and Updated database successfully"
            self.slack_notifier.send_notification(
                type_=self.input.type_,
                user_name=user.get("name", ""),
                sarathi_name=expert.get("name", ""),
                status="success",
                call_link=self.call_link + call_id,
            )

        return Output(
            output_details={},
            output_status=OutputStatus.SUCCESS,
            output_message="Call initiated with callid: " +
            call_id + message + fcm_response + wa_response
        )
