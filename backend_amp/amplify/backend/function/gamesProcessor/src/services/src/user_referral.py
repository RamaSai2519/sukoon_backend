import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.get_prcs.main import GetPRCS
from models.upsert_prc.main import UpsertPRC
from models.list_offers.main import ListOffers
from models.upsert_offer.main import UpsertOffer
from models.validate_prc.main import ValidatePRC
from models.get_referrals.main import GetUserReferrals
from models.list_referrals.main import ListUserReferrals
from shared.models.interfaces import GetReferralsInput, UpsertOfferInput, ListOffersInput, ValidatePRCInput, GetPRCSInput, UpsertPRCInput


class UserReferralService(Resource):

    def get(self) -> dict:
        output = ListUserReferrals().process()
        output = dataclasses.asdict(output)

        return output

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = GetReferralsInput(**input)
        output = GetUserReferrals(input).process()
        output = dataclasses.asdict(output)

        return output


class UpsertOfferService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = UpsertOfferInput(**input)
        output = UpsertOffer(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> dict:
        input_params = request.args
        input = ListOffersInput(**input_params)
        output = ListOffers(input).process()
        output = dataclasses.asdict(output)

        return output


class PRCService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = UpsertPRCInput(**input)
        output = UpsertPRC(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> dict:
        input_params = request.args
        input = GetPRCSInput(**input_params)
        output = GetPRCS(input).process()
        output = dataclasses.asdict(output)

        return output


class ValidatePRCService(Resource):

    def get(self) -> dict:
        input = request.args
        input = ValidatePRCInput(**input)
        output = ValidatePRC(input).process()
        output = dataclasses.asdict(output)

        return output
