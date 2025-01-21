import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.get_sub_plans.main import GetSubPlans
from models.upsert_sub_plan.main import UpsertSubPlan
from models.check_eligibility.main import CheckEligibility
from models.update_user_balance.main import UpdateUserBalance
from shared.models.interfaces import UpdateUserBalanceInput, CheckEligiblilityInput, UpsertSubPlanInput, GetSubPlansInput, Output


class UserBalanceService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = UpdateUserBalanceInput(**input)
        output = UpdateUserBalance(input).process()
        output = dataclasses.asdict(output)

        return output


class CheckEligibilityService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = CheckEligiblilityInput(**input)
        output = CheckEligibility(input).process()
        output = dataclasses.asdict(output)

        return output


class SubPlanService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = UpsertSubPlanInput(**input)
        output = UpsertSubPlan(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> dict:
        input_params = request.args
        input = GetSubPlansInput(**input_params)
        output = GetSubPlans(input).process()
        output = dataclasses.asdict(output)

        return output
