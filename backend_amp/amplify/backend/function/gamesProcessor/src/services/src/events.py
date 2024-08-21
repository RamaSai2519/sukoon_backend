import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.get_events.main import ListEvents
from models.create_event.main import CreateEvent
from models.update_event.main import UpdateEvent
from models.interfaces import EventInput, getEventsInput, Output


class CreateEventsService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = EventInput(**input)
        output = CreateEvent(input).process()
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