import json
import requests
from bson import ObjectId
from datetime import datetime
from shared.models.constants import OutputStatus
from shared.db.calls import get_calls_collection
from models.whatsapp_webhook_event.slack import WASlackNotifier
from shared.models.interfaces import WhatsappWebhookEventInput as Input, Output, WASlackNotifierInput
from shared.db.users import get_user_collection, get_user_webhook_messages_collection, get_user_notification_collection, get_user_whatsapp_feedback_collection, get_user_notification_collection

FIX_CALL_BODY = ["Speak with same Sarathi"]
SCHEDULE_REMINDER_BODY = ["I am available",
                          "Reschedule the call", "Cancel the call"]
COMMON_CALL_REPLY_BODY = ["Connect with Sarathis", "Connect with Experts",
                          "I want something else", "Speak to another Sarathi"]


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input

    def _send_whatsapp_message(self, parameters, phone_number, template_name):
        url = "https://6x4j0qxbmk.execute-api.ap-south-1.amazonaws.com/main/actions/send_whatsapp"

        payload = json.dumps({
            "phone_number": phone_number,
            "template_name": template_name,
            "parameters": parameters
        })

        headers = {
            'Content-Type': 'application/json'
        }
        print(payload)
        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)

    def get_user_id_from_number(self, phone_number):
        phone_number = phone_number[2:]
        user_collection = get_user_collection()
        user = user_collection.find_one({"phoneNumber": phone_number})
        if not user:
            return None, "",""
        user_id = user.get("_id", None)
        source = user.get("source", "")
        name = user.get("name", "")

        return user_id, source, name

    def create_user_webhook_message_id(self, body, user_id, from_number, name):
        slack_notifier = WASlackNotifier(
            from_number=from_number, name=name, body=body)
        slack_notifier.send_notification()
        if not user_id:
            return

        message_data = {
            "body": body,
            "userId": user_id,
            "createdAt": datetime.now()
        }
        user_webhook_messages_collection = get_user_webhook_messages_collection()
        user_webhook_messages_collection.insert_one(message_data)

    def _create_user_feedback_message(self, body, user_id, sarathi_id, call_id):
        user_whatsapp_feedback_collection = get_user_whatsapp_feedback_collection()
        message_data = {
            "body": body,
            "userId": user_id,
            "sarathiId": sarathi_id,
            "callId": call_id,
            "createdAt": datetime.now()

        }
        user_whatsapp_feedback_collection.insert_one(message_data)

    def _get_message_body_and_phone_number_from_message(self):
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

    def _get_status_and_message_id_value(self):
        message_id = status = None
        for entry in self.input.entry:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                for status in value.get('statuses', []):
                    message_id = status.get('id')
                    status_value = status.get('status')
                    # Process or collect the message_id and status_value as needed
                    print(f"ID: {message_id}, Status: {status_value}")
        return message_id, status_value

    def update_user_notification_status(self, message_id, status):
        user_notification_collection = get_user_notification_collection()
        notification = user_notification_collection.find_one(
            {"messageId": message_id})
        if notification:
            notification_id = notification.get("_id")
            user_notification_collection.update_one(
                {"_id": ObjectId(notification_id)},
                {"$set": {"notification_status": status}},
            )

    def _get_feedback_values(self):
        context_id = None
        screen_0_recommend_0 = None

        # Loop through the entries
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

                        # Attempt to parse the response_json
                        try:
                            response_data = json.loads(response_json)
                            screen_0_recommend_0 = response_data.get(
                                'screen_0_recommend_0', None)
                        except json.JSONDecodeError:
                            print("Error decoding JSON response.")

                        # Break after finding the first valid entry
                        if context_id and screen_0_recommend_0:
                            break
        except Exception as e:
            print(f"An error occurred: {e}")
        return context_id, screen_0_recommend_0

    def compute(self):

        body, from_number = self._get_message_body_and_phone_number_from_message()
        if not body:
            context_id, screen_0_recommend_0 = self._get_feedback_values()
            if screen_0_recommend_0:
                message = get_user_notification_collection().find_one(
                    {"messageId": context_id})
                if message:
                    request_meta = json.loads(message.get("requestMeta", ""))
                    sarathi_id = request_meta.get("sarathiId", "")
                    user_id = request_meta.get("userId", "")
                    call_id = request_meta.get("callId", "")
                    self._create_user_feedback_message(
                        screen_0_recommend_0, user_id, sarathi_id, call_id)
            else:
                message_id, status = self._get_status_and_message_id_value()
                if message_id and status:       
                    self.update_user_notification_status(message_id, status)

        if body:
            user_id, source, name = self.get_user_id_from_number(from_number)
            if not user_id:
                self.create_user_webhook_message_id(
                body, "USER_NOT_PRESENT", from_number, "USER_NAME_NOT_PRESENT")
            else:    
                phone_number = from_number[2:]
                self.create_user_webhook_message_id(
                    body, user_id, from_number, name)

            if user_id:
                if body in COMMON_CALL_REPLY_BODY:
                    parameters = {"mobile_number": "9110673203"}
                    self._send_whatsapp_message(
                        parameters, phone_number, template_name="COMMON_CALL_REPLY")

                elif body in FIX_CALL_BODY:
                    parameters = {}
                    self._send_whatsapp_message(
                        parameters, phone_number, template_name="FIX_TIME_REPLY")

                elif body in SCHEDULE_REMINDER_BODY:
                    print("Replied to Schedule Reminder:", body)

                else:
                    parameters = {}
                    user_calls = get_calls_collection(
                    ).count_documents({"user": user_id})
                    if user_calls == 0 and source == "Events":
                        self._send_whatsapp_message(
                            parameters, phone_number, template_name="REGISTERED_USER_ONLY_EVENT_ACTIVE")

                    else:
                        self._send_whatsapp_message(
                            parameters, phone_number, template_name="REGISTERED_USER_QUERY")

            else:
                if body in COMMON_CALL_REPLY_BODY:
                    parameters = {"mobile_number": "9110673203"}
                    self._send_whatsapp_message(
                        parameters, phone_number, template_name="COMMON_CALL_REPLY")

                else:
                    parameters = {}
                    self._send_whatsapp_message(
                        parameters, phone_number, template_name="NON_REGISTERED_USER_QUERY")

        return Output(
            output_details={"body": body, "from_number": from_number},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully received message"
        )
