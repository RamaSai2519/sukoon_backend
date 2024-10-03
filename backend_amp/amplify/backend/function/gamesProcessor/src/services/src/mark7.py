import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.invoke_mark.main import InvokeMark
from models.update_expert_scores.main import UpdateExpertScores
from models.interfaces import UpdateScoresInput, InvokeMarkInput


class UpdateExpertScoresService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = UpdateScoresInput(**input)
        output = UpdateExpertScores(input).process()
        output = dataclasses.asdict(output)

        return output


class InvokeMarkService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = InvokeMarkInput(**input)
        output = InvokeMark(input).process()
        output = dataclasses.asdict(output)

        return output
