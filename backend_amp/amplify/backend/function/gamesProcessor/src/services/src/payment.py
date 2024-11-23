
import json
import dataclasses
from flask import request
from flask_restful import Resource
from shared.models.interfaces import CreatePaymentOrderInput, Output
from models.create_payment_order.main import CreatePaymentOrder


class CreatePaymentOrderService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = CreatePaymentOrderInput(**input)
        output = CreatePaymentOrder(input).process()
        output = dataclasses.asdict(output)

        return output
