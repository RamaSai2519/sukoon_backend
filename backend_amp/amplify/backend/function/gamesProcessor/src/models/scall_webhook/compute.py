import threading
from bson import ObjectId
from shared.models.common import Common
from shared.db.users import get_user_collection
from shared.db.calls import get_calls_collection
from shared.db.experts import get_experts_collections
from shared.helpers.call_webhook import CallWebhookHelper
from shared.models.constants import OutputStatus, CallStatus
from shared.models.interfaces import SCallEndWebhookInput as Input, Call, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.callId = self.input.uuid
        self.call_oid = self.input.suid
        self.collection = get_calls_collection()
        self.users_collection = get_user_collection()
        self.experts_collection = get_experts_collections()
        self.status, self.failed_reason = self.determine_failed_reason_and_status()

    def determine_status(self, cause: str, call_status: str) -> str:
        if call_status == 'missed':
            if cause == 'failed':
                return CallStatus.FAILED
            elif cause == 'cancel':
                return CallStatus.FAILED
            elif cause == 'noanswer':
                return CallStatus.MISSED
        elif call_status == 'answered':
            if int(self.input.duration) > 120:
                return CallStatus.SUCCESSFUL
            return CallStatus.INADEQUATE
        return CallStatus.FAILED

    def determine_failed_reason(self, cause: str) -> str:
        if cause == 'failed':
            return 'expert missed'
        elif cause == 'cancel':
            return 'expert picked and cancelled'
        elif cause == 'noanswer':
            return 'user missed'
        else:
            return cause

    def determine_failed_reason_and_status(self) -> tuple:
        cause = self.input.hangup_cause.lower()
        call_status = self.input.call_status.lower()

        status = self.determine_status(cause, call_status)
        failed_reason = self.determine_failed_reason(cause)
        return status, failed_reason

    def seconds_to_duration_str(self) -> str:
        seconds = int(self.input.duration)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f'{hours:02}:{minutes:02}:{seconds:02}'

    def find_call(self, call_oid: str) -> dict:
        query = {"_id": ObjectId(call_oid)}
        call = self.collection.find_one(query)
        call = Common.clean_dict(call, Call)
        return Call(**call) if call else None

    def update_call(self, call: Call) -> str:
        duration_str = self.seconds_to_duration_str()
        filter = {'callId': call.callId}
        update = {
            '$set': {
                'callId': self.callId,
                'status': self.status,
                'duration': duration_str,
                'failedReason': self.failed_reason,
                'recording_url': self.input.recording_url
            }
        }
        response = self.collection.update_one(filter, update)
        message = 'Call updated, ' if response.modified_count > 0 else 'Call not updated, '
        return message

    def update_schedule(self, call: Call) -> str:
        if call.scheduledId:
            status_str = self.status + ', ' + self.failed_reason
            self.common.update_schedule_status(
                ObjectId(call.scheduledId), status_str)
            return 'Scheduled job updated, '
        return 'Scheduled job not updated, '

    def compute(self) -> Output:
        call = self.find_call(self.call_oid)
        if not call:
            return Output(
                output_status=OutputStatus.FAILURE,
                output_message="Call not found"
            )

        helper = CallWebhookHelper(
            self.callId, int(
                self.input.duration), self.status, self.failed_reason
        )
        threading.Thread(target=helper.compute).start()

        call_message = self.update_call(call)
        schedule_message = self.update_schedule(call)
        message = call_message + schedule_message

        print(self.callId + ' updated: ' + message)
        return Output(output_message="Call processed")
