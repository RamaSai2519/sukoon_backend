
import json
import dataclasses
from flask_restful import Resource
from flask import request
from models.interfaces import SendOTPInput, Output
from models.send_otp.main import SendOTP
from models.interfaces import ValidateOTPInput, Output
from models.validate_otp.main import ValidateOTP


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