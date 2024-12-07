import json
import dataclasses
from flask import request
from flask_restful import Resource
from shared.models.common import Common
from models.admin_schedule.main import AdminSchedules
from models.upsert_schedule.main import UpsertSchedule
from models.get_reschedules.main import GetReSchedules
from models.upsert_recurring_schedules.main import UpsertRecurringSchedules
from shared.models.interfaces import GetScheduledJobsInput, UpsertRecurringSchedulesInput, UpsertScheduleInput, GetReSchedulesInput


class SchedulesService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = UpsertScheduleInput(**input)
        output = UpsertSchedule(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> dict:
        input_params = request.args
        input = GetScheduledJobsInput(**input_params)
        output = AdminSchedules(input).process()
        output = dataclasses.asdict(output)

        return output


class ReSchedulesService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = Common.clean_dict(input, UpsertRecurringSchedulesInput)
        input = UpsertRecurringSchedulesInput(**input)
        output = UpsertRecurringSchedules(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> dict:
        input_params = request.args
        input = GetReSchedulesInput(**input_params)
        output = GetReSchedules(input).process()
        output = dataclasses.asdict(output)

        return output
