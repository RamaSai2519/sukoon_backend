import json
import requests
from models.iprocessor import IProcessor
from configs import CONFIG as CONFIG
from models.whatsapp_notification_helpers.template_setter import (
    WhatsappNotificationTemplateSetter,
)
from models.whatsapp_notification_helpers.queries import update_user_notification_message_id
from http import HTTPStatus
from db.users import get_user_collection



class WhatsappNotification(IProcessor):
    def __init__(self, record):
        self.record = record
        self.request_meta = json.loads(self.record["requestMeta"]["S"])
        self.user_id = self.record["userId"]["S"]
        self.id = self.record["id"]["S"]
        self.notification_type = self.record["notificationType"]["S"]


    def get_user_id_from_number(self, phone_number):
        user_collection = get_user_collection()
        user = user_collection.find_one({"phoneNumber": phone_number})
        if not user:
            return None
        user_id = user.get("_id")
        return user_id

    def send_whatsapp_notification(self, mobile_number, template):
        variables = CONFIG.WHATSAPP_API
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

    def process_document(self):
        mobile_number = self.request_meta.get("phone_number")
        template_name = self.request_meta.get("template_name")
        # user_id = self.get_user_id_from_number(mobile_number)

        parameters = self.request_meta.get("parameters")
        for key, value in parameters.items():
            if type(value) == str:
                parameters[key] = value.strip()
        template_setter_obj = WhatsappNotificationTemplateSetter()
        template_setter_obj.template = (
            parameters,
            template_name
        )
        final_template = template_setter_obj.template

        response = self.send_whatsapp_notification(
            mobile_number, final_template
        )
        message_id = ""
        status = "FAILED"

        if response.status_code == HTTPStatus.OK.value:
            response_json = json.loads(response._content)
            message_id = (response_json.get("messages")[0]).get("id")
            status = "SUCCESS"
            update_user_notification_message_id(self.id, message_id)

        return (status, response.text)

