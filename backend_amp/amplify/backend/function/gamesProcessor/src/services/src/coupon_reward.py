import json
import dataclasses
from flask_restful import Resource
from flask import request
from shared.models.interfaces import CouponRewardInput, Output
from models.coupon_reward.main import CouponReward


class CouponRewardService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = CouponRewardInput(**input)
        output = CouponReward(input).process()
        output = dataclasses.asdict(output)

        return output
