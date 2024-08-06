import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.interfaces import CallInput
from models.make_call.main import MakeCall

class CallService(Resource):

    def post(self):
        input = json.loads(request.get_data())
        input = CallInput(**input)
        output = MakeCall(input).process()
        output = dataclasses.asdict(output)

        return output