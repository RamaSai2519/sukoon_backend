import json
import dataclasses
from flask import request
from flask_restful import Resource
from models.get_wa_options.main import WaOptions
from models.get_wa_history.main import GetWaHistory
from models.handle_admin_wa.main import AdminWhatsapp
from models.send_whatsapp_message.main import SendWhatsappMessage
from models.whatsapp_webhook_event.main import WhatsappWebhookEvent
from models.verify_whatsapp_webhook.main import VerifyWhatsappWebhook
from shared.models.interfaces import WhtasappMessageInput, GetWhatsappWebhookInput, WhatsappWebhookEventInput, GetWaHistoryInput, WaOptionsInput, AdminWaInput


class WhatsappMessageService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = WhtasappMessageInput(**input)
        output = SendWhatsappMessage(input).process()
        output = dataclasses.asdict(output)

        return output


class WhatsappWebhookService(Resource):

    def get(self) -> dict:
        hub_mode = request.args.get('hub.mode')
        hub_challenge = request.args.get('hub.challenge')
        hub_verify_token = request.args.get('hub.verify_token')
        input = GetWhatsappWebhookInput(hub_mode=hub_mode,
                                        hub_challenge=int(hub_challenge),
                                        hub_verify_token=hub_verify_token)
        output = VerifyWhatsappWebhook(input).process()

        return output

    def post(self) -> dict:
        input = json.loads(request.get_data())
        print(input, "whatsapp_webhook")
        input = WhatsappWebhookEventInput(**input)
        output = WhatsappWebhookEvent(input).process()
        output = dataclasses.asdict(output)

        return output


class WhatsappHistoryService(Resource):

    def get(self) -> dict:
        input_params = request.args
        input = GetWaHistoryInput(**input_params)
        output = GetWaHistory(input).process()
        output = dataclasses.asdict(output)

        return output


class AdminWhatsappService(Resource):

    def get(self) -> dict:
        input_params = request.args
        input = WaOptionsInput(**input_params)
        output = WaOptions(input).process()
        output = dataclasses.asdict(output)

        return output

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = AdminWaInput(**input)
        output = AdminWhatsapp(input).process()
        output = dataclasses.asdict(output)

        return output
