import json
import dataclasses
from flask import request
from flask_restful import Resource
from shared.models.interfaces import RecommendExpertInput
from models.recommend_expert.main import RecommendExpert


class RecommendExpertService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = RecommendExpertInput(**input)
        output = RecommendExpert(input).process()
        output = dataclasses.asdict(output)

        return output
