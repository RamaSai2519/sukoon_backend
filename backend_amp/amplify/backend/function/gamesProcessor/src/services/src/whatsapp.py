import json
import dataclasses
from flask import request
from flask_restful import Resource
from shared.interfaces.whatsapp import *
from models.get_wa_refs.main import GetWaRefs
from models.get_wa_options.main import WaOptions
from shared.models.constants import OutputStatus
from models.upsert_wa_ref.main import UpsertWaRef
from models.get_wa_history.main import GetWaHistory
from models.handle_admin_wa.main import AdminWhatsapp
from models.get_wa_templates.main import GetWaTemplates
from models.upsert_wa_templates.main import UpsertWaTemplates
from models.send_whatsapp_message.main import SendWhatsappMessage
from models.whatsapp_webhook_event.main import WhatsappWebhookEvent
from models.verify_whatsapp_webhook.main import VerifyWhatsappWebhook
from shared.models.interfaces import WhtasappMessageInput, GetWhatsappWebhookInput, WhatsappWebhookEventInput, GetWaHistoryInput, WaOptionsInput, AdminWaInput, UpsertWaRefInput, GetWaRefsInput, Output, GetWaTemplatesInput


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


class WhatsappRefService(Resource):

    def post(self) -> dict:
        input = json.loads(request.get_data())
        input = UpsertWaRefInput(**input)
        output = UpsertWaRef(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> dict:
        input_params = request.args
        input = GetWaRefsInput(**input_params)
        output = GetWaRefs(input).process()
        output = dataclasses.asdict(output)

        return output


class WhatsappTemplateService(Resource):

    def set_input(self, doc: dict) -> UpsertWaTemplateInput:
        language = Language(
            code=Enums.LanguageCode[doc["template"]["language"]["code"].upper()])
        components = self.process_components(
            doc["template"].get("components", []))
        template = Template(
            name=doc["template"]["name"], language=language, components=components)
        return UpsertWaTemplateInput(template_name=doc["template_name"], template=template)

    def process_components(self, components_data: list) -> list:
        components = []
        for comp in components_data:
            parameters = self.process_parameters(comp.get("parameters", []))
            component_type = Enums.ComponentType[comp["type"].upper()]
            sub_type = Enums.SubType[comp["sub_type"].upper(
            )] if "sub_type" in comp else None
            components.append(Component(type=component_type, index=comp.get(
                "index"), sub_type=sub_type, parameters=parameters))
        return components

    def process_parameters(self, parameters_data: list) -> list:
        parameters = []
        for param in parameters_data:
            parameter_type = Enums.ParameterType[param["type"].upper()]
            if parameter_type == Enums.ParameterType.TEXT:
                parameters.append(
                    Parameter(type=parameter_type, text=param["text"]))
            elif parameter_type == Enums.ParameterType.IMAGE:
                parameters.append(
                    Parameter(type=parameter_type, image=Image(link=param["image"]["link"])))
            elif parameter_type == Enums.ParameterType.VIDEO:
                parameters.append(
                    Parameter(type=parameter_type, video=Video(link=param["video"]["link"])))
            elif parameter_type == Enums.ParameterType.DOCUMENT:
                parameters.append(Parameter(type=parameter_type, document=Document(
                    filename=param["document"]["filename"], link=param["document"]["link"])))
        return parameters

    def post(self) -> dict:
        input = json.loads(request.get_data())
        try:
            input = self.set_input(input)
        except Exception as e:
            return Output(
                output_status=OutputStatus.FAILURE,
                output_message=f'Invalid value passed: {str(e).lower()}'
            ).__dict__
        output = UpsertWaTemplates(input).process()
        output = dataclasses.asdict(output)

        return output

    def get(self) -> dict:
        input_params = request.args
        input = GetWaTemplatesInput(**input_params)
        output = GetWaTemplates(input).process()
        output = dataclasses.asdict(output)

        return output
