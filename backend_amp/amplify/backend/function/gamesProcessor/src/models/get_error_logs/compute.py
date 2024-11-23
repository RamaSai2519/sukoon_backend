from shared.models.interfaces import GetErrorLogsInput as Input, Output
from shared.db.admins import get_error_logs_collection
from shared.models.constants import OutputStatus
from shared.models.common import Common
from datetime import datetime


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_error_logs_collection()

    def compute(self) -> Output:
        query = {'callId': self.input.callId}
        log: dict = self.collection.find_one(query)

        if not log:
            return Output(
                output_status=OutputStatus.FAILURE,
                output_message="Call Logs not found",
                output_details={}
            )

        logs: list = log.get("logs", [])
        logs = [Common.jsonify(log) for log in logs]
        logs = sorted(logs, key=lambda x: x.get(
            'time', datetime.min), reverse=True)

        return Output(
            output_status=OutputStatus.SUCCESS,
            output_message="Data fetched successfully",
            output_details={"data": logs}
        )
