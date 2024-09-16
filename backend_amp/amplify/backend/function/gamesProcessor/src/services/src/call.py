import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.make_call.main import MakeCall
from models.interfaces import CallInput, Output


class CallService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = CallInput(**input)
        output = MakeCall(input).process()
        output = dataclasses.asdict(output)

        return output


class CallWebhookService(Resource):

    def post(self):
        data = request.json
        print(data)
        return data
