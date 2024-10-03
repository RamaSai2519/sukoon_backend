import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.get_user.main import GetUser
from models.get_leads.main import GetLeads
from models.save_remark.main import SaveRemark
from models.upsert_user.main import UpsertUser
from models.create_event_user.main import CreateEventUser
from models.get_engagement_data.main import GetEngagementData
from models.upsert_engagement_data.main import UpsertEngagementData
from models.interfaces import User, GetUsersInput, EventUserInput, GetLeadsInput, SaveRemarkInput, GetEngagementDataInput, UpsertEngagementDataInput


class UserService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = User(**input)
        output = UpsertUser(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> dict:
        input_params = request.args
        input = GetUsersInput(**input_params)
        output = GetUser(input).process()
        output = dataclasses.asdict(output)

        return output


class CreateEventUserService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = EventUserInput(**input)
        output = CreateEventUser(input).process()
        output = dataclasses.asdict(output)

        return output


class LeadsService(Resource):

    def get(self) -> dict:
        input_params = request.args
        input = GetLeadsInput(**input_params)
        output = GetLeads(input).process()
        output = dataclasses.asdict(output)

        return output


class RemarksService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = SaveRemarkInput(**input)
        output = SaveRemark(input).process()
        output = dataclasses.asdict(output)

        return output


class EngagementDataService(Resource):

    def get(self) -> dict:
        input_params = request.args
        input = GetEngagementDataInput(**input_params)
        output = GetEngagementData(input).process()
        output = dataclasses.asdict(output)

        return output

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = UpsertEngagementDataInput(**input)
        output = UpsertEngagementData(input).process()
        output = dataclasses.asdict(output)

        return output
        
