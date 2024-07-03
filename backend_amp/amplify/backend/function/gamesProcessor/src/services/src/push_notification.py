import json
import dataclasses
from flask_restful import Resource
from flask import request
from models.interfaces import WhtasappMessageInput, GetWhatsappWebhookInput, WhatsappWebhookEventInput ,Output
from models.send_whatsapp_message.main import SendWhatsappMessage
from models.verify_whatsapp_webhook.main import VerifyWhatsappWebhook
from models.whatsapp_webhook_event.main import WhatsappWebhookEvent



class PushNotificationService(Resource):
    
    def post(self) -> Output:
        input = json.loads(request.get_data())
        input = WhtasappMessageInput(**input)
        output = SendWhatsappMessage(input).process()
        output = dataclasses.asdict(output)

        return output
    

class FCMTokenService(Resource):
        
    def post(self) -> Output:
        input = json.loads(request.get_data())
        print(input)
        input = WhatsappWebhookEventInput(**input)
        output = WhatsappWebhookEvent(input).process()
        output = dataclasses.asdict(output)

        return output