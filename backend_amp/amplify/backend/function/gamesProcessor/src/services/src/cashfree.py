import json
import dataclasses
from flask_restful import Resource
from flask import request
from shared.models.interfaces import CashfreeWebhookEventInput, Output
from models.cashfree_webhook_event.main import CashfreeWebhookEvent


class CashfreeWebhookService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = CashfreeWebhookEventInput(**input)
        output = CashfreeWebhookEvent(input).process()
        output = dataclasses.asdict(output)

        return output
