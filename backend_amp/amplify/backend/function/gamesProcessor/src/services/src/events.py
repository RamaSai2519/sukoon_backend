import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.get_events.main import ListEvents
from models.update_event.main import UpdateEvent
from models.get_event_users.main import ListEventUsers
from models.upsert_event_config.main import UpsertEvent
from models.interfaces import EventInput, getEventsInput, GetEventUsersInput, Output


class UpsertEventsService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = EventInput(**input)
        output = UpsertEvent(input).process()
        output = dataclasses.asdict(output)

        return output


class UpdateEventService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = EventInput(**input)
        output = UpdateEvent(input).process()
        output = dataclasses.asdict(output)

        return output


class ListEventsService(Resource):

    def get(self) -> Output:
        input_params = request.args
        input = getEventsInput(**input_params)
        output = ListEvents(input).process()
        output = dataclasses.asdict(output)

        return output


class ListEventUsersService(Resource):

    def get(self) -> Output:
        input_params = request.args
        input = GetEventUsersInput(**input_params)
        output = ListEventUsers(input).process()
        output = dataclasses.asdict(output)

        return output
