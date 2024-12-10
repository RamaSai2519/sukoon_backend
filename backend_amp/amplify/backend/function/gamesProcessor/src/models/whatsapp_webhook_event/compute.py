import json
import requests
from bson import ObjectId
from datetime import datetime
from shared.models.common import Common
from shared.configs import CONFIG as config
from shared.models.constants import OutputStatus
from models.whatsapp_webhook_event.slack import WASlackNotifier
from models.whatsapp_webhook_event.chat_helper import ChatHelper
from shared.models.interfaces import WhatsappWebhookEventInput as Input, Output
from shared.db.users import get_user_collection, get_user_webhook_messages_collection, get_user_notification_collection, get_user_whatsapp_feedback_collection, get_user_notification_collection


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.chat_helper = ChatHelper()

    def _send_whatsapp_message(self, parameters, phoneNumber, template_name) -> None:
        url = config.URL + '/actions/send_whatsapp'
        payload = {
            'phoneNumber': phoneNumber,
            'template_name': template_name,
            'parameters': parameters
        }
        response = requests.post(url, json=payload)
        print(response.text)

    def create_lead(self, phoneNumber: str) -> Output:
        url = config.URL + '/actions/user'
        payoad = {'phoneNumber': phoneNumber, 'refSource': 'wa_webhook'}
        response = requests.post(url, json=payoad)
        user_id = Output(**response.json()).output_details.get('_id', None)
        return ObjectId(user_id)

    def get_user_id_from_number(self, phoneNumber: str) -> dict:
        user_collection = get_user_collection()
        user = user_collection.find_one({'phoneNumber': phoneNumber})
        return user

    def create_user_webhook_message_id(self, body, user_id, from_number, name) -> None:
        slack_notifier = WASlackNotifier(
            from_number=from_number, name=name, body=body)
        slack_notifier.send_notification()
        if not user_id:
            return

        message_data = {
            'body': body,
            'userId': user_id,
            'phoneNumber': from_number,
            'createdAt': datetime.now()
        }
        user_webhook_messages_collection = get_user_webhook_messages_collection()
        user_webhook_messages_collection.insert_one(message_data)

    def _create_user_feedback_message(self, body, user_id, sarathi_id, call_id) -> None:
        user_whatsapp_feedback_collection = get_user_whatsapp_feedback_collection()
        message_data = {
            'body': body,
            'userId': user_id,
            'sarathiId': sarathi_id,
            'callId': call_id,
            'createdAt': datetime.now()
        }
        user_whatsapp_feedback_collection.insert_one(message_data)

    def _get_message_body_and_phoneNumber_from_message(self) -> tuple:
        body = from_number = None
        for entry in self.input.entry:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                for message in value.get('messages', []):
                    body = message.get('text', {}).get('body')
                    from_number = message.get('from')
                    if not body:
                        body = message.get('button', {}).get('text')
        return body, from_number

    def _get_status_and_message_id_value(self) -> tuple:
        message_id = status = None
        for entry in self.input.entry:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                for status in value.get('statuses', []):
                    message_id = status.get('id')
                    status_value = status.get('status')
        return message_id, status_value

    def update_user_notification_status(self, message_id, status) -> None:
        user_notification_collection = get_user_notification_collection()
        notification = user_notification_collection.find_one(
            {'messageId': message_id})
        if notification:
            notification_id = notification.get('_id')
            user_notification_collection.update_one(
                {'_id': ObjectId(notification_id)},
                {'$set': {'notification_status': status}},
            )

    def _get_feedback_values(self) -> tuple:
        context_id = None
        screen_0_recommend_0 = None

        try:
            for entry in self.input.entry:
                for change in entry.get('changes', []):
                    messages = change.get('value', {}).get('messages', [])
                    for message in messages:
                        context = message.get('context', {})
                        context_id = context.get('id', None)

                        interactive = message.get('interactive', {})
                        nfm_reply = interactive.get('nfm_reply', {})
                        response_json = nfm_reply.get('response_json', '{}')

                        try:
                            response_data = json.loads(response_json)
                            screen_0_recommend_0 = response_data.get(
                                'screen_0_recommend_0', None)
                        except json.JSONDecodeError:
                            print('Error decoding JSON response.')

                        if context_id and screen_0_recommend_0:
                            break
        except Exception as e:
            print(f'An error occurred: {e}')
        return context_id, screen_0_recommend_0

    def chat(self, phoneNumber: str, body: str) -> str:
        url = config.MARK_URL + '/flask/chat'
        payload = {
            'phoneNumber': phoneNumber, 'prompt': body,
            'context': self.chat_helper.context,
            'system_message': self.chat_helper.get_system_message(phoneNumber)
        }
        response = requests.post(url, json=payload)
        response = Output(**response.json()).output_details.get('response')

        return response

    def send_reply(self, from_number: str, text: str) -> requests.Response:
        url = config.WHATSAPP_API['URL']
        payload = {
            'messaging_product': 'whatsapp',
            'to': from_number,
            'text': {
                'body': text.replace('**', '*')
            }
        }
        token = config.WHATSAPP_API['ACCESS_TOKEN']
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.post(url, headers=headers, json=payload)

        return response

    def compute(self) -> Output:
        body, from_number = self._get_message_body_and_phoneNumber_from_message()
        if not body:
            context_id, screen_0_recommend_0 = self._get_feedback_values()
            if screen_0_recommend_0:
                message = get_user_notification_collection().find_one(
                    {'messageId': context_id})
                if message:
                    request_meta = json.loads(message.get('requestMeta', ''))
                    sarathi_id = request_meta.get('sarathiId', '')
                    user_id = request_meta.get('userId', '')
                    call_id = request_meta.get('callId', '')
                    self._create_user_feedback_message(
                        screen_0_recommend_0, user_id, sarathi_id, call_id)
            else:
                message_id, status = self._get_status_and_message_id_value()
                if message_id and status:
                    self.update_user_notification_status(message_id, status)

            return Output(
                output_details={'body': body, 'from_number': from_number},
                output_status=OutputStatus.SUCCESS,
                output_message='Successfully received message'
            )

        phoneNumber = from_number[2:]
        user = self.get_user_id_from_number(phoneNumber)
        user_id = user.get('_id', None) if user else None
        name = user.get('name', 'Unknown') if user else 'Unknown'
        if not user_id:
            user_id = self.create_lead(phoneNumber)

        gpt_response = self.chat(phoneNumber, body)
        reply_response = self.send_reply(from_number, gpt_response)
        print(reply_response.text)

        self.create_user_webhook_message_id(body, user_id, from_number, name)

        return Output(
            output_details={'body': body, 'from_number': from_number},
            output_status=OutputStatus.SUCCESS,
            output_message='Successfully received message'
        )
