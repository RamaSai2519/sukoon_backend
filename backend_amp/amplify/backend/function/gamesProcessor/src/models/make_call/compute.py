import pytz
import time
import threading
from bson import ObjectId
from datetime import datetime
from dataclasses import asdict
from typing import Tuple, Dict
from .servetel import MakeServeTelCall
from shared.models.common import Common
from .knowlarity import MakeKnowlarityCall
from shared.db.users import get_user_collection
from shared.db.calls import get_calls_collection
from models.make_call.slack import SlackNotifier
from shared.models.constants import OutputStatus
from shared.db.experts import get_experts_collections
from models.make_call.notifications import Notifications
from shared.models.interfaces import CallInput as Input, Output, Call, CallerInput


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

    def prep_call(self, user_id: ObjectId, expert_id: ObjectId, call_id: str) -> dict:
        call = Call(user=user_id, expert=expert_id, callId=call_id, user_requested=self.input.user_requested, scheduledId=self.input.scheduledId,
                    initiatedTime=datetime.now(pytz.utc), status="initiated", type=self.input.type_, direction='outbound')
        return asdict(call)

    def _update_db(self, user_id: ObjectId, expert_id: ObjectId, call_id: str = None) -> bool:
        user_update = self.users_collection.update_one(
            {"_id": user_id}, {"$set": {"isBusy": True}})
        if user_update.modified_count == 0:
            print("Failed to update user")

        query = {'_id': expert_id}
        expert = self.experts_collection.find_one(query)
        number = expert.get('phoneNumber')
        expert_update = Common.update_expert_isbusy(number, True)
        if expert_update != True:
            print("Failed to update expert")

        call = self.prep_call(user_id, expert_id, call_id)
        call = Common.filter_none_values(call)
        call_insert = self.calls_collection.insert_one(call)
        if call_insert.inserted_id is None:
            print("Failed to insert call")
            return None

        return call_insert.inserted_id

    def compute(self) -> Output:
        user_id = ObjectId(self.input.user_id)
        expert_id = ObjectId(self.input.expert_id)

        user, expert = self.get_users(user_id, expert_id)
        if not user or not expert:
            return Output(
                output_status=OutputStatus.FAILURE,
                output_message="User or Expert not found"
            )

        fcm_response = self.notifier.send_fcm_notification(user, expert)
        wa_response = self.notifier.send_wa_notification(user, expert)

        if self.input.wait == True:
            time.sleep(15)

        payload = CallerInput(
            user_number=user["phoneNumber"],
            expert_number=expert["phoneNumber"],
            expert_type=expert.get("type", "internal")
        )

        call_id = self._update_db(user_id, expert_id)
        payload.call_id = str(call_id)
        caller = MakeServeTelCall(payload)
        threading.Thread(target=caller._make_call).start()

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
        self.slack_notifier.send_notification(
            type_=self.input.type_,
            user_name=user.get("name", ""),
            sarathi_name=expert.get("name", ""),
            status="success",
            call_link=self.call_link + str(call_id),
        )

        return Output(
            output_details=Common.jsonify({'call_id': call_id}),
            output_message="Call initiated with callid: " +
            str(call_id) + fcm_response + wa_response
        )
