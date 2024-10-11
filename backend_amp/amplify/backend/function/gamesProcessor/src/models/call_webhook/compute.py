import json
import requests
from typing import Union
from models.common import Common
from db.users import get_user_collection
from db.calls import get_calls_collection
from db.experts import get_experts_collections
from models.constants import OutputStatus, application_json_header
from db_queries.mutations.scheduled_job import update_scheduled_job_status
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
        call = Common.clean_dict(call, Call)
        return Call(**call)

    def find_call(self, callId: str) -> Union[Call, None]:
        call = self.calls_collection.find_one({"callId": callId})
        call = self.prep_call(call) if call else None
        return call

    def find_user(self, call: Call) -> Union[User, None]:
        user = self.users_collection.find_one({"_id": call.user})
        user = Common.clean_dict(user, User)
        return User(**user) if user else None

    def find_expert(self, call: Call) -> Union[Expert, None]:
        expert = self.experts_collection.find_one({"_id": call.expert})
        expert = Common.clean_dict(expert, Expert)
        return Expert(**expert) if expert else None

    def update_user(self, call: Call, expert: Expert, user: User) -> str:
        filter = {"_id": call.user}
        update_values = {"isBusy": False}
        if expert and user and expert.type != "internal" and self.common.duration_str_to_seconds(self.input.call_duration) > 600 and user.numberOfCalls > 0 and user.isPaidUser == False:
            update_values["numberOfCalls"] = user.numberOfCalls - 1
        update = {"$set": update_values}
        response = self.users_collection.update_one(filter, update)
        message = "User updated, " if response.modified_count > 0 else "User not updated, "
        return message

    def update_expert(self, call: Call) -> str:
        filter = {"_id": call.expert}
        update = {"$set": {"isBusy": False}}
        response = self.experts_collection.update_one(filter, update)
        message = "Expert updated, " if response.modified_count > 0 else "Expert not updated, "
        return message

    def determine_status(self, call_transfer_status: str, call_status: str) -> str:
        if call_transfer_status == "missed":
            status = "missed"
        elif call_status == "connected":
            if self.common.duration_str_to_seconds(self.input.call_duration) > 120:
                status = "successful"
            else:
                status = "inadequate"
        else:
            status = "failed"
        return status

    def determine_failed_reason(self, call_transfer_status: str) -> str:
        if call_transfer_status == "missed":
            failed_reason = "user missed"
        elif call_transfer_status in ["not connected", "none"]:
            failed_reason = "expert missed"
        elif call_transfer_status == "did not process":
            failed_reason = "knowlarity missed"
        else:
            failed_reason = ""
        return failed_reason

    def determine_failed_reason_and_status(self) -> tuple:
        call_transfer_status = self.input.call_transfer_status.lower()
        call_status = self.input.call_status.lower()

        status = self.determine_status(call_transfer_status, call_status)
        failed_reason = self.determine_failed_reason(call_transfer_status)
        return status, failed_reason

    def update_call(self, call: Call) -> str:
        status, failed_reason = self.determine_failed_reason_and_status()
        filter = {"callId": call.callId}
        update = {
            "$set": {
                "status": status,
                "failedReason": failed_reason,
                "duration": self.input.call_duration,
                "recording_url": self.input.callrecordingurl,
                "transferDuration": self.input.call_transfer_duration
            }
        }
        response = self.calls_collection.update_one(filter, update)
        message = "Call updated, " if response.modified_count > 0 else "Call not updated, "
        return message

    def update_schedule(self, call: Call) -> str:
        if call.scheduledId:
            status, reason = self.determine_failed_reason_and_status()
            status_str = status + ', ' + reason
            update_scheduled_job_status(call.scheduledId, status_str)
            return "Scheduled job updated, "
        return "Scheduled job not updated, "

    def send_feedback_message(self, call: Call, expert: Expert, user: User) -> str:
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
            "parameters": {"user_name": user.name, "sarathi_name": expert.name}
        }
        response = requests.request(
            "POST", self.url, headers=application_json_header, data=json.dumps(payload))
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

        user = self.find_user(call)
        expert = self.find_expert(call)
        call_message = self.update_call(call)
        schedule_message = self.update_schedule(call)
        user_message = self.update_user(call, expert, user)
        expert_message = self.update_expert(call)
        feedback_message = "Feedback message not sent"

        call = self.find_call(callId)
        duration = self.common.duration_str_to_seconds(call.duration)
        if call.status == "successful" and duration > 120 and expert.type != "internal":
            feedback_message = self.send_feedback_message(call, expert, user)

        final_message = call_message + schedule_message + \
            user_message + expert_message + feedback_message

        return Output(
            output_details={},
            output_status=OutputStatus.SUCCESS,
            output_message=final_message
        )
