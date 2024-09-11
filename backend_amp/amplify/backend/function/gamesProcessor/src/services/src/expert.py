import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.get_slots.main import GetSlots
from models.get_experts.main import ListExperts
from models.upsert_expert.main import UpsertExpert
from models.create_applicant.main import CreateApplicant
from models.interfaces import Expert, GetExpertsInput, ApplicantInput, GetSlotsInput, Output


class ExpertService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = Expert(**input)
        output = UpsertExpert(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> Output:
        input_params = request.args
        input = GetExpertsInput(**input_params)
        output = ListExperts(input).process()
        output = dataclasses.asdict(output)

        return output


class ApplicantService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = ApplicantInput(**input)
        output = CreateApplicant(input).process()
        output = dataclasses.asdict(output)

        return output

class SlotsService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = GetSlotsInput(**input)
        output = GetSlots(input).process()
        output = dataclasses.asdict(output)

        return output