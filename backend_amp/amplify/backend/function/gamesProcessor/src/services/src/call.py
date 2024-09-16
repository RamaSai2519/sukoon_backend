import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.make_call.main import MakeCall
from models.call_webhook.main import CallWebhook
from models.interfaces import CallInput, WebhookInput


class CallService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = CallInput(**input)
        output = MakeCall(input).process()
        output = dataclasses.asdict(output)

        return output


class CallWebhookService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = WebhookInput(**input)
        output = CallWebhook(input).process()
        output = dataclasses.asdict(output)

        return output
