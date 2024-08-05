import json
import dataclasses
from flask_restful import Resource
from flask import request
from models.interfaces import UpsertRegisteredUserInput, Output
from models.upsert_registered_user.main import UpsertRegisteredUser

from models.interfaces import CreateNonRegisteredUserInput, Output
from models.create_non_registered_user.main import CreateNonRegisteredUser

from models.interfaces import GetUserInput, Output
from models.get_user.main import GetUser


class UserService(Resource):
    
    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = UpsertRegisteredUserInput(**input)
        output = UpsertRegisteredUser(input).process()
        output = dataclasses.asdict(output)

        return output
    
    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = CreateNonRegisteredUserInput(**input)
        output = CreateNonRegisteredUser(input).process()
        output = dataclasses.asdict(output)

        return output
    
    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = GetUserInput(**input)
        output = GetUser(input).process()
        output = dataclasses.asdict(output)

        return output