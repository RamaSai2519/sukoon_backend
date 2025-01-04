import json
import requests
from http import HTTPStatus
from datetime import datetime
from shared.configs import CONFIG as config
from shared.models.constants import OutputStatus
from .template_setter import WhatsappNotificationTemplateSetter
from shared.models.interfaces import WhtasappMessageInput as Input, Output
from shared.db.users import get_user_collection, get_user_notification_collection


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input

    def get_user(self, phone_number):
        user_collection = get_user_collection()
        user = user_collection.find_one({"phoneNumber": phone_number})
        if not user:
            return None
        return user

    def create_user_notification_message_id(self, message_id, status, user_id):
        user_collection = get_user_notification_collection()
        message_data = {
            "userId": user_id,
            "status": status,
            "templateName": self.input.template_name,
            "messageId": message_id,
            "requestMeta": self.input.request_meta,
            "createdAt": datetime.now()
        }
        user_collection.insert_one(message_data)

    def send_whatsapp_notification(self, mobile_number, template):
        variables = config.WHATSAPP_API
        whatsapp_api_url = variables.get("URL")
        auth_token = variables.get("ACCESS_TOKEN")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}",
        }

        body = {
            "messaging_product": "whatsapp",
            "type": "template",
            "to": "91" + mobile_number,
            "template": template,
        }
        response = requests.request(
            "POST",
            url=whatsapp_api_url,
            data=json.dumps(body),
            headers=headers,
        )
        return response

    def compute(self) -> Output:
        user = self.get_user(self.input.phone_number)
        if user:
            user_wa = user.get('wa_opt_out', False)
            if user_wa:
                return Output(
                    output_details={},
                    output_status=OutputStatus.SUCCESS,
                    output_message="User has opted out of whatsapp notifications"
                )
        user_id = user.get('_id', None) if user else None

        parameters = self.input.parameters
        for key, value in parameters.items():
            if type(value) == str:
                parameters[key] = value.strip()
        template_setter_obj = WhatsappNotificationTemplateSetter()
        template_setter_obj.template = (
            parameters,
            self.input.template_name
        )
        final_template = template_setter_obj.template

        mobile_number = self.input.phone_number
        response = self.send_whatsapp_notification(
            mobile_number, final_template
        )
        message_id = ""
        status = "FAILED"

        if response.status_code == HTTPStatus.OK.value:
            response_json = json.loads(response._content)
            message_id = (response_json.get("messages")[0]).get("id")
            status = "SUCCESS"
        if user_id:
            self.create_user_notification_message_id(
                message_id, status, user_id)

        return Output(
            output_details={"response": response.text},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully sent whatsapp message"
        )
