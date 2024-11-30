import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.list_offers.main import ListOffers
from models.upsert_offer.main import UpsertOffer
from models.get_referrals.main import GetUserReferrals
from models.list_referrals.main import ListUserReferrals
from shared.models.interfaces import GetReferralsInput, UpsertOfferInput, ListOffersInput


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
