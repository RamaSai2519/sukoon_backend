import json
import dataclasses
from flask import request
from flask_restful import Resource
from shared.models.interfaces import UpdateScoresInput
from models.update_expert_scores.main import UpdateExpertScores


class UpdateExpertScoresService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = UpdateScoresInput(**input)
        output = UpdateExpertScores(input).process()
        output = dataclasses.asdict(output)

        return output
