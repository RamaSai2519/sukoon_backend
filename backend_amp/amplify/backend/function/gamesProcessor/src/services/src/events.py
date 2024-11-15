import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.get_events.main import ListEvents
from models.get_event_users.main import ListEventUsers
from models.upsert_event_config.main import UpsertEvent
from models.upsert_contribute_event.main import UpsertContributeEvent
from models.create_contribute_interest.main import CreateContributeInterest
from models.interfaces import Event, GetEventsInput, GetEventUsersInput, ContributeEvent, CreateContributeInterestInput, Output


class UpsertEventsService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = Event(**input)
        output = UpsertEvent(input).process()
        output = dataclasses.asdict(output)

        return output


class ListEventsService(Resource):

    def get(self) -> Output:
        input_params = request.args
        input = GetEventsInput(**input_params)
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


class UpsertContributeEventService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = ContributeEvent(**input)
        output = UpsertContributeEvent(input).process()
        output = dataclasses.asdict(output)

        return output


class CreateContributeInterestService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = CreateContributeInterestInput(**input)
        output = CreateContributeInterest(input).process()
        output = dataclasses.asdict(output)

        return output
