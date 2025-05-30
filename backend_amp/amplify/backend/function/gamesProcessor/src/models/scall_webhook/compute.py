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
        self.call_oid = self.input.suid
        self.callId = self.input.call_id
        self.collection = get_calls_collection()
        self.users_collection = get_user_collection()
        self.user_fails = ['noanswer', 'chanunavail']
        self.experts_collection = get_experts_collections()
        self.expert_fails = ['failed', 'cancel', 'no answer']
        self.status, self.failed_reason = self.determine_failed_reason_and_status()

    def determine_status(self, cause: str, call_status: str) -> str:
        missed_causes = self.user_fails
        failed_causes = self.expert_fails
        if call_status == 'missed':
            if cause in failed_causes:
                if self.input.direction == 'inbound':
                    return CallStatus.MISSED
                else:
                    return CallStatus.FAILED
            if cause in missed_causes:
                if self.input.direction == 'inbound':
                    return CallStatus.FAILED
                else:
                    return CallStatus.MISSED
        elif call_status == 'answered':
            if int(self.input.duration) > 120:
                return CallStatus.SUCCESSFUL
            return CallStatus.INADEQUATE
        return CallStatus.FAILED

    def determine_failed_reason(self, cause: str) -> str:
        direction = self.input.direction
        cause_mapping = {
            'failed': 'missed',
            'no answer': 'declined',
            'cancel': 'cancelled',
            'noanswer': 'missed',
            'chanunavail': 'declined'
        }
        if cause in cause_mapping:
            if direction == 'inbound':
                if cause in self.user_fails:
                    message = f'expert {cause_mapping[cause]}'
                else:
                    message = f'user {cause_mapping[cause]}'
            else:
                if cause in self.user_fails:
                    message = f'user {cause_mapping[cause]}'
                else:
                    message = f'expert {cause_mapping[cause]}'
        else:
            message = cause
        return message

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
        if call_oid:
            query = {"_id": ObjectId(call_oid)}
        else:
            query = {'callId': self.callId}
        call = self.collection.find_one(query)
        call = Common.clean_dict(call, Call)
        return Call(**call) if call else None

    def update_call(self, call: Call) -> str:
        duration_str = self.seconds_to_duration_str()
        filter = {'_id': call._id}
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

        call_message = self.update_call(call)
        schedule_message = self.update_schedule(call)
        message = call_message + schedule_message
        helper = CallWebhookHelper(
            self.callId, int(
                self.input.duration), self.status, self.failed_reason
        )
        threading.Thread(target=helper.compute).start()

        print(self.callId + ' updated: ' + message)
        return Output(output_message="Call processed")
