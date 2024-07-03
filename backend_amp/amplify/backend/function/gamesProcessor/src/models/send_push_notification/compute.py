import requests
import json
from models.interfaces import PushNotificationInput as Input, Output
from models.constants import OutputStatus
from configs import CONFIG as CONFIG
from .template_setter import (
    WhatsappNotificationTemplateSetter,
)
from http import HTTPStatus
from db.users import get_user_collection, get_user_notification_collection
from datetime import datetime


class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input


    def get_user_id_from_number(self, phone_number):
        user_collection = get_user_collection()
        user = user_collection.find_one({"phoneNumber": phone_number})
        if not user:
            return None
        user_id = user.get("_id")
        return user_id

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
        variables = CONFIG.PUSH_NOTIFICATION_API
        push_notification_api_url = variables.get("URL")
        auth_token = variables.get("ACCESS_TOKEN")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"key={auth_token}",
        }

        body = {
            "to": "<Device FCM token>",
            "notification": {
                "title": "Check this Mobile (title)",
                "body": "Rich Notification testing (body)",
            },
            "data": {
                "actonType": "internal",
                "url": "<url of media image>",
                "dl": "<deeplink action on tap of notification>"
            }
        }
        response = requests.request(
            "POST",
            url=push_notification_api_url,
            data=json.dumps(body),
            headers=headers,
        )
        return response

    def compute(self):
        user_id = self.get_user_id_from_number(self.input.phone_number)

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
            self.create_user_notification_message_id(message_id, status, user_id)


        return Output(
            output_details={"response": response.text},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched game config"
        )