import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.send_otp.main import SendOTP
from models.admin_auth.main import AdminAuth
from models.validate_otp.main import ValidateOTP
from shared.models.interfaces import SendOTPInput, ValidateOTPInput, AdminAuthInput, Output


class SendOTPService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = SendOTPInput(**input)
        output = SendOTP(input).process()
        output = dataclasses.asdict(output)

        return output


class ValidateOTPService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = ValidateOTPInput(**input)
        output = ValidateOTP(input).process()
        output = dataclasses.asdict(output)

        return output


class AdminAuthService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = AdminAuthInput(**input)
        output = AdminAuth(input).process()
        output = dataclasses.asdict(output)

        return output
