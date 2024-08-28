import json
import dataclasses
from flask_restful import Resource
from flask import request
from models.interfaces import ScheduledJobInput, Output
from models.create_scheduled_job.main import CreateScheduledJob
from models.update_scheduled_job.main import UpdateScheduledJob


class CreateScheduledJobsService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = ScheduledJobInput(**input)
        output = CreateScheduledJob(input).process()
        output = dataclasses.asdict(output)

        return output


class UpdateScheduledJobsService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = ScheduledJobInput(**input)
        output = UpdateScheduledJob(input).process()
        output = dataclasses.asdict(output)

        return output
