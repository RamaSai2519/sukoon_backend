import requests
import json
import os
from models.interfaces import PushNotificationInput as Input, Output
from models.constants import OutputStatus
from configs import CONFIG as CONFIG
from http import HTTPStatus
from db.users import get_user_notification_collection
from datetime import datetime
from google.oauth2 import service_account
import google.auth.transport.requests

SCOPES = ['https://www.googleapis.com/auth/firebase.messaging'] 
class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input

    def create_user_notification_message_id(self, status, user_id):
        user_collection = get_user_notification_collection()
        message_data = {
            "userId": user_id,
            "status": status,
            "notificationType": "PUSH_NOTIFICATION",
            "createdAt": datetime.now()
        }
        user_collection.insert_one(message_data)

    def get_access_token(self):
        """Retrieve a valid access token that can be used to authorize requests.

        :return: Access token.
        """
        file_path = os.path.join(os.path.dirname(__file__), 'service-account.json')
        credentials = service_account.Credentials.from_service_account_file(file_path, scopes=SCOPES)
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

        status = OutputStatus.FAILURE
        if response.status_code == HTTPStatus.OK.value:
            status = OutputStatus.SUCCESS

        if self.input.user_id:
            self.create_user_notification_message_id(status, self.input.user_id)

        return Output(
            output_details={"response": response.text},
            output_status=status,
            output_message="Successfully send push notification"
        )