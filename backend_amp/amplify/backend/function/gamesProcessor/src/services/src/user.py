import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.get_user.main import GetUser
from models.upsert_user.main import UpsertUser
from models.create_event_user.main import CreateEventUser
from models.interfaces import User, GetUsersInput, EventUserInput, Output


class UserService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = User(**input)
        output = UpsertUser(input).process()
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
