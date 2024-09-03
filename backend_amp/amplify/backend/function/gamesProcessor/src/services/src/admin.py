import json
import dataclasses
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from models.interfaces import SaveFCMTokenInput, Output
from models.save_fcm_token.main import SaveAdminFCMToken


class AdminFCMService(Resource):

    @jwt_required()
    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = SaveFCMTokenInput(**input)
        output = SaveAdminFCMToken(input).process()
        output = dataclasses.asdict(output)

        return output
