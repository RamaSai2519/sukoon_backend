import json
import dataclasses
from flask_restful import Resource
from flask import request
from models.interfaces import PushNotificationInput,Output
from models.send_push_notification.main import SendPushNotification



class PushNotificationService(Resource):
    
    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = PushNotificationInput(**input)
        output = SendPushNotification(input).process()
        output = dataclasses.asdict(output)

        return output
    

# class FCMTokenService(Resource):
        
#     def post(self) -> Output:
#         input = json.loads(request.get_data())
#         print(input)
#         input = WhatsappWebhookEventInput(**input)
#         output = WhatsappWebhookEvent(input).process()
#         output = dataclasses.asdict(output)

#         return output