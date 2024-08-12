
import json
import dataclasses
from flask_restful import Resource
from flask import request
from models.interfaces import CreatePaymentOrderInput, Output
from models.create_payment_order.main import CreatePaymentOrder


class CreatePaymentOrderService(Resource):
    
    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = CreatePaymentOrderInput(**input)
        output = CreatePaymentOrder(input).process()
        output = dataclasses.asdict(output)

        return output
    