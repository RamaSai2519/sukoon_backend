import json
import dataclasses
from flask import request
from flask_restful import Resource
from shared.models.common import Common
from models.get_slots.main import GetSlots
from flask_jwt_extended import jwt_required
from models.get_timings.main import GetTimings
from models.get_experts.main import ListExperts
from models.get_categories.main import Categories
from models.upsert_expert.main import UpsertExpert
from models.get_applicants.main import GetApplicants
from models.update_timings.main import UpdateTimings
from models.create_applicant.main import CreateApplicant
from shared.models.interfaces import Expert, CategoriesInput, GetExpertsInput, ApplicantInput, GetSlotsInput, GetTimingsInput, UpdateTimingsInput, TimingsRow, GetApplicantsInput, RecommendExpertInput


class ExpertService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = Common.clean_dict(input, Expert)
        input = Expert(**input)
        output = UpsertExpert(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> dict:
        input_params = request.args
        input = Common.clean_dict(input_params, GetExpertsInput)
        input = GetExpertsInput(**input_params)
        output = ListExperts(input).process()
        output = dataclasses.asdict(output)

        return output


class ApplicantService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = ApplicantInput(**input)
        output = CreateApplicant(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> dict:
        input_params = request.args
        input = GetApplicantsInput(**input_params)
        output = GetApplicants(input).process()
        output = dataclasses.asdict(output)

        return output


class SlotsService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = GetSlotsInput(**input)
        output = GetSlots(input).process()
        output = dataclasses.asdict(output)

        return output


class TimingService(Resource):

    def get(self) -> dict:
        input = request.args
        input = GetTimingsInput(**input)
        output = GetTimings(input).process()
        output = dataclasses.asdict(output)

        return output

    @jwt_required()
    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = {"expertId": input["expertId"],
                 "row": TimingsRow(**input["row"])}
        input = UpdateTimingsInput(**input)
        output = UpdateTimings(input).process()
        output = dataclasses.asdict(output)

        return output


class CategoryService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = CategoriesInput(**input)
        output = Categories(input).process()
        output = dataclasses.asdict(output)

        return output
