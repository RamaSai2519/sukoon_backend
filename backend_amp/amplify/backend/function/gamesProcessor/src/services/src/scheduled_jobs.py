import json
import dataclasses
from flask_restful import Resource
from flask import request
from models.interfaces import CreateScheduledJobInput, Output
from models.create_scheduled_job.main import CreateScheduledJob


class ScheduledJobsService(Resource):
    
    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = CreateScheduledJobInput(**input)
        output = CreateScheduledJob(input).process()
        output = dataclasses.asdict(output)

        return output