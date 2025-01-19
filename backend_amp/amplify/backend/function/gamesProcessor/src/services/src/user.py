import json
import dataclasses
from flask import request
from flask_restful import Resource
from shared.models.common import Common
from models.get_user.main import GetUser
from flask_jwt_extended import jwt_required
from models.save_remark.main import SaveRemark
from models.upsert_user.main import UpsertUser
from models.redeem_offer.main import RedeemOffer
from models.upsert_event_user.main import UpsertEventUser
from models.get_engagement_data.main import GetEngagementData
from models.upsert_phone_config.main import UpsertPhoneConfig
from models.upsert_engagement_data.main import UpsertEngagementData
from models.get_user_status_options.main import GetUserStatusOptions
from shared.models.interfaces import (
    Persona, User, GetUsersInput, EventUserInput,
    SaveRemarkInput, GetEngagementDataInput, UpsertEngagementDataInput,
    PhoneConfigInput, GetUserStatusesInput, RedeemOfferInput, Demographics, Psychographics
)


class UserService(Resource):

    def prepare_data(self, input: dict) -> dict:
        if input.get('customerPersona'):
            demographics = input.get(
                'customerPersona', {}).get('demographics', {})
            psychographics = input.get(
                'customerPersona', {}).get('psychographics', {})
            demographics = Common.clean_dict(demographics, Demographics)
            psychographics = Common.clean_dict(psychographics, Psychographics)
            input['customerPersona']['demographics'] = Demographics(
                **demographics)
            input['customerPersona']['psychographics'] = Psychographics(
                **psychographics)

            persona = input.get('customerPersona', {})
            persona = Common.clean_dict(persona, Persona)
            input['customerPersona'] = Persona(**persona)
        input = Common.clean_dict(input, User)

        return User(**input)

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = self.prepare_data(input)
        output = UpsertUser(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> dict:
        input_params = request.args
        input = GetUsersInput(**input_params)
        output = GetUser(input).process()
        output = dataclasses.asdict(output)

        return output


class PhoneConfigService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = PhoneConfigInput(**input)
        output = UpsertPhoneConfig(input).process()
        output = dataclasses.asdict(output)

        return output


class UpsertEventUserService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = EventUserInput(**input)
        output = UpsertEventUser(input).process()
        output = dataclasses.asdict(output)

        return output


class RemarkService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = SaveRemarkInput(**input)
        output = SaveRemark(input).process()
        output = dataclasses.asdict(output)

        return output


class EngagementDataService(Resource):

    @jwt_required()
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


class UserStatusOptionsService(Resource):

    def get(self) -> dict:
        input_params = request.args
        input = GetUserStatusesInput(**input_params)
        output = GetUserStatusOptions(input).process()
        output = dataclasses.asdict(output)

        return output


class RedeemOfferService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = RedeemOfferInput(**input)
        output = RedeemOffer(input).process()
        output = dataclasses.asdict(output)

        return output
