import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.make_call.main import StCall
from shared.models.interfaces import CallInput


class CallService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = CallInput(**input)
        output = StCall(input).process()
        output = dataclasses.asdict(output)

        return output
