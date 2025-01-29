import threading
from typing import Union
from bson import ObjectId
from shared.models.common import Common
from shared.db.calls import get_calls_collection
from shared.db.experts import get_experts_collections
from shared.helpers.call_webhook import CallWebhookHelper
from shared.models.constants import OutputStatus, CallStatus
from shared.models.interfaces import WebhookInput as Input, Call, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.calls_collection = get_calls_collection()
        self.experts_collection = get_experts_collections()
        self.duration_secs = self.common.duration_str_to_seconds(
            input.call_duration)
        self.status, self.failed_reason = self.determine_failed_reason_and_status()

    def determine_status(self, call_transfer_status: str, call_status: str) -> str:
        if call_transfer_status == 'missed':
            status = CallStatus.MISSED
        elif call_status == 'connected':
            if self.duration_secs > 120:
                status = CallStatus.SUCCESSFUL
            else:
                status = CallStatus.INADEQUATE
        else:
            status = CallStatus.FAILED
        return status

    def determine_failed_reason(self, call_transfer_status: str) -> str:
        if call_transfer_status == 'missed':
            failed_reason = 'user missed'
        elif call_transfer_status in ['not connected', 'none']:
            failed_reason = 'expert missed'
        elif call_transfer_status == 'did not process':
            failed_reason = 'knowlarity missed'
        else:
            failed_reason = ''
        return failed_reason

    def determine_failed_reason_and_status(self) -> tuple:
        call_transfer_status = self.input.call_transfer_status.lower()
        call_status = self.input.call_status.lower()

        status = self.determine_status(call_transfer_status, call_status)
        failed_reason = self.determine_failed_reason(call_transfer_status)
        return status, failed_reason

    def find_call(self, callId: str) -> Union[Call, None]:
        call = self.calls_collection.find_one({'callId': callId})
        call = Common.clean_dict(call, Call)
        return Call(**call) if call else None

    def update_call(self, call: Call) -> str:
        filter = {'callId': call.callId}
        update = {
            '$set': {
                'status': self.status,
                'failedReason': self.failed_reason,
                'duration': self.input.call_duration,
                'recording_url': self.input.callrecordingurl,
                'transferDuration': self.input.call_transfer_duration
            }
        }
        response = self.calls_collection.update_one(filter, update)
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
        callId = self.input.call_uuid.replace('_0', '')
        call = self.find_call(callId)
        if not call:
            return Output(
                output_status=OutputStatus.FAILURE,
                output_message=f'Call not found with callId: {callId}'
            )

        helper = CallWebhookHelper(
            callId, self.duration_secs, self.status, self.failed_reason)
        threading.Thread(target=helper.compute).start()

        call_message = self.update_call(call)
        schedule_message = self.update_schedule(call)
        message = call_message + schedule_message

        print(callId + ' updated: ' + message)
        return Output(output_message='Call processed')
