import json
import dataclasses
from flask_restful import Resource
from flask import request
from models.interfaces import PushNotificationInput,Output , UpdateFCMTokenInput
from models.send_push_notification.main import SendPushNotification
from models.update_fcm_token.main import UpdateUserFCMToken



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