import json
import requests
from typing import Union
from models.common import Common
from db.users import get_user_collection
from models.constants import OutputStatus
from db.calls import get_calls_collection
from db.experts import get_experts_collections
from models.interfaces import WebhookInput as Input, Call, Output, User, Expert


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.url = "https://6x4j0qxbmk.execute-api.ap-south-1.amazonaws.com/main/actions/send_whatsapp"
        self.users_collection = get_user_collection()
        self.calls_collection = get_calls_collection()
        self.experts_collection = get_experts_collections()

    def prep_call(self, call: dict) -> Call:
        call["conversationScore"] = call.pop("Conversation Score", None)
        return Call(**call)

    def find_call(self, callId: str) -> Union[Call, None]:
        call = self.calls_collection.find_one({"callId": callId})
        call = self.prep_call(call) if call else None
        return call

    def find_user(self, call: Call) -> Union[User, None]:
        user = self.users_collection.find_one({"_id": call.user})
        return User(**user) if user else None

    def find_expert(self, call: Call) -> Union[Expert, None]:
        expert = self.experts_collection.find_one({"_id": call.expert})
        return Expert(**expert) if expert else None

    def update_user(self, call: Call) -> str:
        filter = {"_id": call.user}
        update = {"$set": {"isBusy": False}}
        response = self.users_collection.update_one(filter, update)
        message = "User updated, " if response.modified_count > 0 else "User not updated, "
        return message

    def update_expert(self, call: Call):
        filter = {"_id": call.expert}
        update = {"$set": {"isBusy": False}}
        response = self.experts_collection.update_one(filter, update)
        message = "Expert updated, " if response.modified_count > 0 else "Expert not updated, "
        return message

    def update_call(self, call: Call):
        filter = {"callId": call.callId}
        update = {
            "$set": {
                "status": ("successfull" if self.input.call_status == "Connected" else "failed"),
                "failedReason": (
                    "call missed" if self.input.call_transfer_status.lower() == "missed"
                    else "call not picked" if self.input.call_transfer_status.lower() == "not connected"
                    else "call not processed" if self.input.call_transfer_status.lower() == "did not process"
                    else ""
                ),
                "duration": self.input.call_duration,
                "recording_url": self.input.callrecordingurl,
                "transferDuration": self.input.call_transfer_duration
            }
        }
        response = self.calls_collection.update_one(filter, update)
        message = "Call updated, " if response.modified_count > 0 else "Call not updated, "
        return message

    def send_feedback_message(self, call: Call):
        user = self.find_user(call)
        expert = self.find_expert(call)
        if not user or not expert:
            return "Feedback message not sent"
        payload = {
            "template_name": "FEEDBACK_SURVEY",
            "phone_number": user.phoneNumber,
            "request_meta": json.dumps({
                "sarathiId": str(expert._id),
                "callId": call.callId,
                "userId": str(user._id)
            }),
            "parameters": {
                "user_name": user.name,
                "sarathi_name": expert.name,
            }
        }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request(
            "POST", self.url, headers=headers, data=json.dumps(payload)
        )
        print(response.text, "feedback")
        message = "Feedback message sent" if response.status_code == 200 else "Feedback message not sent"
        return message

    def compute(self) -> Output:
        callId = self.input.call_uuid.replace("_0", "")
        call = self.find_call(callId)
        if not call:
            return Output(
                output_details={},
                output_status=OutputStatus.FAILURE,
                output_message=f"Call not found with callid: {callId}"
            )

        call_message = self.update_call(call)
        user_message = self.update_user(call)
        expert_message = self.update_expert(call)
        feedback_message = "Feedback message not sent"

        call = self.find_call(callId)
        duration = self.common.duration_str_to_seconds(call.duration)
        if self.input.call_status == "Connected" and duration > 120:
            feedback_message = self.send_feedback_message(call)

        final_message = call_message + user_message + expert_message + feedback_message
        print(final_message, "final")

        return Output(
            output_details={},
            output_status=OutputStatus.SUCCESS,
            output_message=final_message
        )
