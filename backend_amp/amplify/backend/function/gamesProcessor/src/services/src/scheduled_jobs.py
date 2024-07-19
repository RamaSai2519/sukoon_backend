import json
import dataclasses
from flask_restful import Resource
from flask import request
from models.interfaces import FetchShortsInput, Output
from models.get_shorts.main import GetShorts


class ScheduledJobs(Resource):
    
    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = FetchShortsInput(**input)
        output = GetShorts(input).process()
        output = dataclasses.asdict(output)

        return output