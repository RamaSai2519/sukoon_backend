import json
import dataclasses
from flask import request
from flask_restful import Resource
from shared.models.common import Common
from models.escalate.main import Escalate
from models.get_calls.main import GetCalls
from models.make_call.main import MakeCall
from models.call_webhook.main import CallWebhook
from shared.models.interfaces import CallInput, WebhookInput, GetCallsInput, Escalation, EachEscalation


class CallService(Resource):

    def get(self) -> dict:
        input_params = request.args
        input = GetCallsInput(**input_params)
        output = GetCalls(input).process()
        output = dataclasses.asdict(output)

        return output

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = CallInput(**input)
        output = MakeCall(input).process()
        output = dataclasses.asdict(output)

        return output


class CallWebhookService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = Common.clean_dict(input, WebhookInput)
        input = WebhookInput(**input)
        output = CallWebhook(input).process()
        output = dataclasses.asdict(output)

        return output


class EscalationService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input['escalations'] = [EachEscalation(
            **each) for each in input['escalations']]
        input = Escalation(**input)
        output = Escalate(input).process()
        output = dataclasses.asdict(output)

        return output
