import json
import requests
import threading
from bson import ObjectId
from datetime import datetime
from shared.models.common import Common
from shared.configs import CONFIG as config
from shared.db.whatsapp import get_wa_refs_collection
from shared.models.constants import OutputStatus, test_numbers
from models.whatsapp_webhook_event.slack import WASlackNotifier
from shared.models.interfaces import WhatsappWebhookEventInput as Input, Output
from shared.db.users import get_user_collection, get_user_webhook_messages_collection, get_user_notification_collection, get_user_whatsapp_feedback_collection


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.users_collection = get_user_collection()
        self.refs_collection = get_wa_refs_collection()
        self.notifications_collection = get_user_notification_collection()

    def _send_whatsapp_message(self, parameters, phoneNumber, template_name) -> None:
        url = config.URL + '/actions/send_whatsapp'
        payload = {
            'phone_number': phoneNumber,
            'template_name': template_name,
            'parameters': parameters
        }
        response = requests.post(url, json=payload)
        print(response.text)

    def determine_refSource(self, body: str) -> str:
        query = {'message': body.strip()}
        ref = self.refs_collection.find_one(query)
        return ref.get('source', 'wa_webhook') if ref else 'wa_webhook'

    def create_lead(self, phoneNumber: str, refSource: str) -> Output:
        url = config.URL + '/actions/user'
        payoad = {'phoneNumber': phoneNumber, 'refSource': refSource}
        response = requests.post(url, json=payoad)
        user_id = Output(**response.json()).output_details.get('_id', None)
        return ObjectId(user_id)

    def get_user_id_from_number(self, phoneNumber: str) -> dict:
        query = {'phoneNumber': phoneNumber}
        user = self.users_collection.find_one(query)
        return user

    def create_user_webhook_message_id(self, body, user_id, from_number, name) -> None:
        if from_number not in test_numbers:
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
        notification = self.notifications_collection.find_one(
            {'messageId': message_id})
        if notification:
            notification_id = notification.get('_id')
            self.notifications_collection.update_one(
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
        url = config.ARK_URL + '/ark'
        payload = {
            'phoneNumber': phoneNumber, 'prompt': body,
            'context': 'wa_webhook', 'send_reply': True
        }
        requests.post(url, json=payload)
        print('ARK will respond to the user.')

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
        print(response.text, 'reply')

        return response

    def handle_static_replies(self, user: dict, body: str) -> str:
        stop_promotions = 'stop promotions'
        if stop_promotions in body.lower().strip():
            query = {'_id': user.get('_id')}
            projection = {'$set': {'wa_opt_out': True}}
            self.users_collection.update_one(query, projection)
            return 'You have successfully unsubscribed from promotions.'
        else:
            return None

    def _reply_to_feedback(self, phoneNumber: str, expert_id: str) -> None:
        expert_name = self.common.get_expert_name(ObjectId(expert_id))
        parameters = {'sarathi_name': expert_name.replace('sarathi ', '')}
        template_name = 'SARATHI_SUCCESSFUL_CALL'
        self._send_whatsapp_message(parameters, phoneNumber, template_name)

    def compute(self) -> Output:
        body, from_number = self._get_message_body_and_phoneNumber_from_message()
        if not body:
            context_id, screen_0_recommend_0 = self._get_feedback_values()
            if screen_0_recommend_0:
                query = {'messageId': context_id}
                message = self.notifications_collection.find_one(query)
                if message:
                    request_meta = json.loads(message.get('requestMeta', ''))
                    sarathi_id = request_meta.get('sarathiId', '')
                    user_id = request_meta.get('userId', '')
                    call_id = request_meta.get('callId', '')
                    self._create_user_feedback_message(
                        screen_0_recommend_0, user_id, sarathi_id, call_id)
                    self._reply_to_feedback(from_number[2:], sarathi_id)
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
        user_id = user.get('_id') if user else None
        if not user_id:
            refSource = self.determine_refSource(body)
            user_id = self.create_lead(phoneNumber, refSource)
            user = self.get_user_id_from_number(phoneNumber)

        name = user.get('name', 'Unknown')
        if user.get('isBlocked', False) == False:
            static_reply = self.handle_static_replies(user, body)
            if static_reply:
                reply_response = self.send_reply(from_number, static_reply)
                print(reply_response.text, 'reply_response')
            else:
                threading.Thread(target=self.chat, args=(
                    phoneNumber, body)).start()

        self.create_user_webhook_message_id(body, user_id, from_number, name)

        return Output(
            output_details={'body': body, 'from_number': from_number},
            output_status=OutputStatus.SUCCESS,
            output_message='Successfully received message'
        )
