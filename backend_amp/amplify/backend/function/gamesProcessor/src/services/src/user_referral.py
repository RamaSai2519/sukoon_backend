import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.get_referrals.main import GetUserReferrals
from shared.models.interfaces import Output, GetReferralsInput
from models.list_referrals.main import ListUserReferrals


class UserReferralService(Resource):

    def get(self) -> Output:
        output = ListUserReferrals().process()
        output = dataclasses.asdict(output)

        return output

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = GetReferralsInput(**input)
        output = GetUserReferrals(input).process()
        output = dataclasses.asdict(output)

        return output
