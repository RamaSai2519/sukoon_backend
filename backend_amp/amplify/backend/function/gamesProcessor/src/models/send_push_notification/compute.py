from models.interfaces import PushNotificationInput as Input, Output
from firebase_admin import credentials, messaging
from models.constants import OutputStatus
from configs import CONFIG as config
import firebase_admin
import os


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input

    def initialize_firebase_admin(self) -> None:
        file_path = os.path.join(os.path.dirname(
            __file__), 'service-account.json')
        if not firebase_admin._apps:
            cred = credentials.Certificate(file_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://games-sukoon-app-default-rtdb.firebaseio.com'
            })

    def send_notification_fcm(self, token, body, image_url, title, user_id, sarathi_id, type_, action='') -> None:
        message = messaging.Message(
            token=str(token),
            notification=messaging.Notification(
                body=body,
                image=image_url,
                title=title
            ),
            data={
                'userId': user_id,
                'sarathiId': sarathi_id,
                'type': type_,
                'action': action
            }
        )

        response = messaging.send(message)
        return response

    def compute(self) -> Output:
        self.initialize_firebase_admin()
        token = self.input.token
        body = self.input.body
        image_url = self.input.image_url
        title = self.input.title
        user_id = self.input.user_id
        sarathi_id = self.input.sarathi_id
        type_ = self.input.type_
        action = self.input.action

        response = self.send_notification_fcm(
            token, body, image_url, title, user_id, sarathi_id, type_, action
        )

        return Output(
            output_details=response,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully sent push notification"
        )
