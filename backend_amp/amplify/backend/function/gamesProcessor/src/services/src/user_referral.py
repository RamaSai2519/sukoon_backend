import json
import dataclasses
from flask_restful import Resource
from flask import request
from models.interfaces import UserReferralInput, Output
from models.user_referral.main import UserReferral


class UserReferralService(Resource):
    
    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = UserReferralInput(**input)
        output = UserReferral(input).process()
        output = dataclasses.asdict(output)

        return output