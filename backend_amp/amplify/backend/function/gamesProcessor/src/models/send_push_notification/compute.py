import requests
import json
from models.interfaces import PushNotificationInput as Input, Output
from models.constants import OutputStatus
from configs import CONFIG as CONFIG
# from .template_setter import (
#     WhatsappNotificationTemplateSetter,
# )
from http import HTTPStatus
from db.users import get_user_collection, get_user_notification_collection
from datetime import datetime
from google.oauth2 import service_account
import google.auth.transport.requests

SCOPES = ['https://www.googleapis.com/auth/firebase.messaging'] 
class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input

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

    def get_access_token(self):
        """Retrieve a valid access token that can be used to authorize requests.

        :return: Access token.
        """
        credentials = service_account.Credentials.from_service_account_file(
            '/Users/apple/work/sukoon_backend/backend_amp/amplify/backend/function/gamesProcessor/src/models/send_push_notification/service-account.json', scopes=SCOPES)
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        return credentials.token

    def send_push_notification(self):
        variables = CONFIG.PUSH_NOTIFICATION_API
        push_notification_api_url = variables.get("URL")
        token = self.get_access_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        body = {
            "message":{
                "token": self.input.fcm_token,
                "notification":{
                    "body": self.input.body,
                    "title": self.input.title
                }
            }
        }
        response = requests.request(
            "POST",
            url=push_notification_api_url,
            data=json.dumps(body),
            headers=headers,
        )
        print(response.text)
        return response

    def compute(self):
        response = self.send_push_notification()

        if response.status_code == HTTPStatus.OK.value:
            response_json = json.loads(response._content)
            message_id = (response_json.get("messages")[0]).get("id")
            status = "SUCCESS"
        # if user_id:
        #     self.create_user_notification_message_id(message_id, status, user_id)


        return Output(
            output_details={"response": response.text},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched game config"
        )