import json
import dataclasses
from flask import request
from flask_restful import Resource

from models.interfaces import GetUsersInput
from models.get_user.main import GetUser

from models.interfaces import EventUserInput, Output
from models.create_event_user.main import CreateEventUser


class UserService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = GetUsersInput(**input)
        output = GetUser(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> Output:
        input_params = request.args
        input = GetUsersInput(**input_params)
        output = GetUser(input).process()
        output = dataclasses.asdict(output)

        return output


class CreateEventUserService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = EventUserInput(**input)
        output = CreateEventUser(input).process()
        output = dataclasses.asdict(output)

        return output
