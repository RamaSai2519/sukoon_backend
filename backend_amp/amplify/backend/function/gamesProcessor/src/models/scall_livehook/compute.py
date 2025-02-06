from bson import ObjectId
from shared.models.common import Common
from shared.db.calls import get_calls_collection
from shared.models.constants import OutputStatus
from shared.models.interfaces import SCallLivehookInput as Input, Call, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.call_oid = self.input.suid
        self.callId = self.input.call_id
        self.collection = get_calls_collection()

    def find_call(self, call_oid: str) -> dict:
        query = {"_id": ObjectId(call_oid)}
        call = self.collection.find_one(query)
        call = Common.clean_dict(call, Call)
        return Call(**call) if call else None

    def update_call(self, call: Call) -> str:
        filter = {'callId': call.callId}
        update = {
            '$set': {
                'callId': self.callId,
                'status': self.input.call_status
            }
        }
        response = self.collection.update_one(filter, update)
        message = 'Call updated, ' if response.modified_count > 0 else 'Call not updated, '
        return message

    def update_schedule(self, call: Call) -> str:
        if call.scheduledId:
            status_str = self.input.call_status
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

        print(self.callId + ' updated: ' + message)
        return Output(output_message="Status updated")
