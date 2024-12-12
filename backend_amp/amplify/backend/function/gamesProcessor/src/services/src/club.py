import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.get_club_interests.main import GetInterests
from models.create_club_interest.main import CreateClubInterest
from shared.models.interfaces import CreateClubInterestInput, GetClubInterestsInput


class ClubService(Resource):

    def get(self) -> dict:
        input_params = request.args
        input = GetClubInterestsInput(**input_params)
        output = GetInterests(input).process()
        output = dataclasses.asdict(output)

        return output

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = CreateClubInterestInput(**input)
        output = CreateClubInterest(input).process()
        output = dataclasses.asdict(output)

        return output
