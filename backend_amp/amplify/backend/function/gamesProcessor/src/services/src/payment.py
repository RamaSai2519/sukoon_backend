
import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.get_payments.main import GetPayments
from models.create_payment_order.main import CreatePaymentOrder
from shared.models.interfaces import CreatePaymentOrderInput, GetPaymentsInput


class CreatePaymentOrderService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = CreatePaymentOrderInput(**input)
        output = CreatePaymentOrder(input).process()
        output = dataclasses.asdict(output)

        return output


class PaymentsService(Resource):

    def get(self) -> dict:
        input = request.args
        input = GetPaymentsInput(**input)
        output = GetPayments(input).process()
        output = dataclasses.asdict(output)

        return output
