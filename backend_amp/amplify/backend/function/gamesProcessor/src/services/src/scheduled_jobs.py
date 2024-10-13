import json
import dataclasses
from flask_restful import Resource
from flask import request
from models.admin_schedule.main import AdminSchedules
from models.create_scheduled_job.main import CreateScheduledJob
from models.update_scheduled_job.main import UpdateScheduledJob
from models.interfaces import ScheduledJobInput, GetScheduledJobsInput


class CreateScheduledJobsService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = ScheduledJobInput(**input)
        output = CreateScheduledJob(input).process()
        output = dataclasses.asdict(output)

        return output


class UpdateScheduledJobsService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = ScheduledJobInput(**input)
        output = UpdateScheduledJob(input).process()
        output = dataclasses.asdict(output)

        return output


class GetSchedulesService(Resource):

    def get(self) -> dict:
        input_params = request.args
        input = GetScheduledJobsInput(**input_params)
        output = AdminSchedules(input).process()
        output = dataclasses.asdict(output)

        return output
