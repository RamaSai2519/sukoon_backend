import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.s3_upload.main import S3Upload
from flask_jwt_extended import jwt_required
from models.get_error_logs.main import GetLogs
from models.save_fcm_token.main import SaveAdminFCMToken
from shared.models.interfaces import SaveFCMTokenInput, UploadInput, GetErrorLogsInput


class AdminFCMService(Resource):

    @jwt_required()
    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = SaveFCMTokenInput(**input)
        output = SaveAdminFCMToken(input).process()
        output = dataclasses.asdict(output)

        return output


class UploadService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = UploadInput(**input)
        output = S3Upload(input).process()
        output = dataclasses.asdict(output)

        return output


class LogsService(Resource):

    def get(self) -> dict:
        input_params = request.args
        input = GetErrorLogsInput(**input_params)
        output = GetLogs(input).process()
        output = dataclasses.asdict(output)

        return output
