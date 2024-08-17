from models.interfaces import WhatsappWebhookEventInput as Input, Output
from models.constants import OutputStatus
from db.users import get_user_collection, get_user_webhook_messages_collection, get_user_notification_collection, get_user_whatsapp_feedback_collection
from db.calls import get_calls_collection
from datetime import datetime
import requests, json

COMMON_CALL_REPLY_BODY = ["Connect with Sarathis", "Connect with Experts", "I want something else", "Speak to another Sarathi"]
FIX_CALL_BODY = ["Speak with same Sarathi"]

class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input


    def _send_whatsapp_message(self, parameters, phone_number, template_name):
        url = "https://6x4j0qxbmk.execute-api.ap-south-1.amazonaws.com/main/actions"

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
            return None, ""
        user_id = user.get("_id")
        source = user.get("source", "")

        return user_id, source

    def create_user_webhook_message_id(self, body, user_id):
        user_webhook_messages_collection = get_user_webhook_messages_collection()
        message_data = {
            "body": body,
            "userId": user_id,
            "createdAt": datetime.now()

        }
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
        for entry in self.input.entry:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                for message in value.get('messages', []):
                    body = message.get('text', {}).get('body')
                    from_number = message.get('from')
                    if not body:
                        body = message.get('button', {}).get('text')
        return body, from_number
    
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
                            screen_0_recommend_0 = response_data.get('screen_0_recommend_0', None)
                        except json.JSONDecodeError:
                            print("Error decoding JSON response.")

                        # Break after finding the first valid entry
                        if context_id and screen_0_recommend_0:
                            break
        except Exception as e:
            print(f"An error occurred: {e}")
        return context_id, screen_0_recommend_0
    
    def compute(self):

        body , from_number = self._get_message_body_and_phone_number_from_message()
        if not body:
            context_id, screen_0_recommend_0 = self._get_feedback_values()
            if screen_0_recommend_0:
                message = get_user_notification_collection().find_one({"messageId": context_id})
                if message:
                    request_meta = json.loads(message.get("requestMeta", ""))
                    sarathi_id = request_meta.get("sarathiId", "")
                    user_id = request_meta.get("userId", "")
                    call_id = request_meta.get("callId", "")
                    self._create_user_feedback_message(screen_0_recommend_0, user_id, sarathi_id, call_id)
            
        if body:
            user_id, source = self.get_user_id_from_number(from_number)
            phone_number = from_number[2:]

            if user_id:
                if body in COMMON_CALL_REPLY_BODY:
                    parameters = {"mobile_number": "9110673203"}
                    self._send_whatsapp_message(parameters, phone_number, template_name= "COMMON_CALL_REPLY")

                elif body in FIX_CALL_BODY:
                    parameters = {}
                    self._send_whatsapp_message(parameters, phone_number, template_name= "FIX_TIME_REPLY")

                else:
                    parameters = {}
                    user_calls = get_calls_collection().count_documents({"user": user_id})
                    if user_calls == 0  and source == "Events":
                        self._send_whatsapp_message(parameters, phone_number, template_name= "REGISTERED_USER_ONLY_EVENT_ACTIVE")

                    else:
                        self._send_whatsapp_message(parameters, phone_number, template_name= "REGISTERED_USER_QUERY")

                self.create_user_webhook_message_id(body, user_id)

            else:
                if body in COMMON_CALL_REPLY_BODY:
                    parameters = {"mobile_number": "9110673203"}
                    self._send_whatsapp_message(parameters, phone_number, template_name= "COMMON_CALL_REPLY")

                else:
                    parameters = {}
                    self._send_whatsapp_message(parameters, phone_number, template_name= "NON_REGISTERED_USER_QUERY")

        return Output(
            output_details= {"body": body, "from_number": from_number},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched game config"
        )