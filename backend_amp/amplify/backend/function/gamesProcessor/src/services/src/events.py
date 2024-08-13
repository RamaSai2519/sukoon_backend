import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.create_event.main import CreateEvent
from models.update_event.main import UpdateEvent
from models.interfaces import EventInput, Output


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
