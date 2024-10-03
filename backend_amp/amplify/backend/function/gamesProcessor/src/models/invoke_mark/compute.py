import json
import boto3
from models.common import Common
from db.calls import get_calls_collection
from models.constants import OutputStatus
from models.interfaces import InvokeMarkInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_calls_collection()

    def invoke_mark(self, call: dict):
        client = boto3.client('lambda')
        response = client.invoke(
            FunctionName="mark7-main",
            InvocationType='RequestResponse',
            Payload=json.dumps({"call": call})
        )
        response_payload = json.loads(response['Payload'].read())
        return response_payload

    def find_call(self) -> dict:
        call = self.collection.find_one({"callId": self.input.callId})
        return call if call else None

    def compute(self) -> Output:
        call = self.find_call()
        if call:
            call = Common.jsonify(call)
            response = self.invoke_mark(call)
            return Output(
                output_details=response,
                output_status=OutputStatus.SUCCESS,
                output_message="Successfully invoked mark7"
            )
        return Output(
            output_details={},
            output_status=OutputStatus.FAILURE,
            output_message="Call not found"
        )
