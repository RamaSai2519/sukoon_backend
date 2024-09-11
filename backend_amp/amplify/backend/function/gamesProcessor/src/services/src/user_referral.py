import json
import dataclasses
from flask_restful import Resource
from flask import request
from models.interfaces import Output
from models.list_referrals.main import UserReferrals


class UserReferralService(Resource):

    def get(self) -> Output:
        output = UserReferrals().process()
        output = dataclasses.asdict(output)

        return output
