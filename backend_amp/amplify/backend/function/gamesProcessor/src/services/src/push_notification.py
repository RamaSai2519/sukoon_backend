import json
import dataclasses
from flask_restful import Resource
from flask import request
from shared.models.interfaces import PushNotificationInput, Output, UpdateFCMTokenInput, UpsertFCMTemplateInput
from models.send_push_notification.main import SendPushNotification
from models.update_fcm_token.main import UpdateUserFCMToken
from models.upsert_fcm_template.main import UpsertFCMTemplate

class PushNotificationService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = PushNotificationInput(**input)
        output = SendPushNotification(input).process()
        output = dataclasses.asdict(output)

        return output


class FCMTokenService(Resource):

    def post(self) -> Output:
        input = json.loads(request.get_data())
        print(input)
        input = UpdateFCMTokenInput(**input)
        output = UpdateUserFCMToken(input).process()
        output = dataclasses.asdict(output)

        return output

class FCMTemplateService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = UpsertFCMTemplateInput(**input)
        output= UpsertFCMTemplate(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> dict:
        output = UpsertFCMTemplate().process()
        
