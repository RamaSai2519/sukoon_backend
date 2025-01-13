import json
import requests
import threading
from typing import Union
from bson import ObjectId
from shared.models.common import Common
from shared.configs import CONFIG as config
from shared.db.experts import get_experts_collections
from shared.db.calls import get_calls_collection, get_escalations_collection
from shared.db.users import get_user_collection, get_user_notification_collection
from shared.models.interfaces import WebhookInput as Input, Call, Output, User, Expert
from shared.models.constants import OutputStatus, application_json_header, CallStatus, non_sarathi_types


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.users_collection = get_user_collection()
        self.calls_collection = get_calls_collection()
        self.url = config.URL + '/actions/send_whatsapp'
        self.experts_collection = get_experts_collections()
        self.escalations_collection = get_escalations_collection()
        self.user_notifications_collection = get_user_notification_collection()
        self.duration_secs = self.common.duration_str_to_seconds(
            input.call_duration)

        self.status, self.failed_reason = self.determine_failed_reason_and_status()

    def determine_status(self, call_transfer_status: str, call_status: str) -> str:
        if call_transfer_status == 'missed':
            status = CallStatus.MISSED
        elif call_status == 'connected':
            if self.duration_secs > 120:
                status = CallStatus.SUCCESSFUL
            else:
                status = CallStatus.INADEQUATE
        else:
            status = CallStatus.FAILED
        return status

    def determine_failed_reason(self, call_transfer_status: str) -> str:
        if call_transfer_status == 'missed':
            failed_reason = 'user missed'
        elif call_transfer_status in ['not connected', 'none']:
            failed_reason = 'expert missed'
        elif call_transfer_status == 'did not process':
            failed_reason = 'knowlarity missed'
        else:
            failed_reason = ''
        return failed_reason

    def determine_failed_reason_and_status(self) -> tuple:
        call_transfer_status = self.input.call_transfer_status.lower()
        call_status = self.input.call_status.lower()

        status = self.determine_status(call_transfer_status, call_status)
        failed_reason = self.determine_failed_reason(call_transfer_status)
        return status, failed_reason

    def find_call(self, callId: str) -> Union[Call, None]:
        call = self.calls_collection.find_one({'callId': callId})
        call = Common.clean_dict(call, Call)
        return Call(**call)

    def find_user(self, call: Call) -> Union[User, None]:
        user = self.users_collection.find_one({'_id': call.user})
        user = Common.clean_dict(user, User)
        return User(**user) if user else None

    def find_expert(self, call: Call) -> Union[Expert, None]:
        expert = self.experts_collection.find_one({'_id': call.expert})
        expert = Common.clean_dict(expert, Expert)
        return Expert(**expert) if expert else None

    def update_user(self, call: Call, expert: Expert, user: User) -> str:
        filter = {'_id': call.user}
        update_values = {'isBusy': False}
        conditions = [
            user.numberOfCalls > 0,
            self.duration_secs > 600,
            user.isPaidUser == False,
            expert.type not in non_sarathi_types
        ]
        if all(conditions):
            update_values['numberOfCalls'] = user.numberOfCalls - 1
        update = {'$set': update_values}
        response = self.users_collection.update_one(filter, update)
        message = 'User updated, ' if response.modified_count > 0 else 'User not updated, '
        if 'numberOfCalls' in update_values and response.modified_count > 0:
            message += 'User call limit updated to {new} from {old}, '
            message = message.format(
                new=user.numberOfCalls - 1, old=user.numberOfCalls)
        return message

    def update_expert(self, call: Call) -> str:
        filter = {'_id': call.expert}
        update = {'$set': {'isBusy': False}}
        response = self.experts_collection.update_one(filter, update)
        message = 'Expert updated, ' if response.modified_count > 0 else 'Expert not updated, '
        return message

    def update_call(self, call: Call) -> str:
        filter = {'callId': call.callId}
        update = {
            '$set': {
                'status': self.status,
                'failedReason': self.failed_reason,
                'duration': self.input.call_duration,
                'recording_url': self.input.callrecordingurl,
                'transferDuration': self.input.call_transfer_duration
            }
        }
        response = self.calls_collection.update_one(filter, update)
        message = 'Call updated, ' if response.modified_count > 0 else 'Call not updated, '
        return message

    def update_schedule(self, call: Call) -> str:
        if call.scheduledId:
            status_str = self.status + ', ' + self.failed_reason
            self.common.update_schedule_status(
                ObjectId(call.scheduledId), status_str)
            return 'Scheduled job updated, '
        return 'Scheduled job not updated, '

    def send_feedback_message(self, call: Call, expert: Expert, user: User) -> str:
        if call.status == 'successful' and self.duration_secs > 120 and expert.type not in non_sarathi_types:
            if not user or not expert:
                return 'Feedback message not sent as user or expert not found'
            payload = {
                'template_name': 'FEEDBACK_SURVEY',
                'phone_number': user.phoneNumber,
                'request_meta': json.dumps({
                    'sarathiId': str(expert._id),
                    'callId': call.callId,
                    'userId': str(user._id)
                }),
                'parameters': {'user_name': user.name, 'sarathi_name': expert.name}
            }
            response = requests.request(
                'POST', self.url, headers=application_json_header, data=json.dumps(payload))
            message = 'Feedback message sent' if response.status_code == 200 else 'Feedback message not sent'
            return message
        return 'Feedback message not sent'

    def send_promo_message(self, call: Call, expert: Expert, user: User) -> str:
        query = {'userId': user._id, 'templateName': 'PROMO_TEMPLATE'}
        notification = self.user_notifications_collection.find_one(query)
        if call.status == 'successful' and expert.type == 'internal' and self.duration_secs > 120 and not notification:
            if not user or not expert:
                return 'Promo message not sent as user or expert not found'
            payload = {
                'template_name': 'PROMO_TEMPLATE',
                'phone_number': user.phoneNumber,
                'request_meta': json.dumps({'expert_name': expert.name, 'callId': call.callId, 'user_name': user.name or user.phoneNumber}),
                'parameters': {'image_link': 'https://sukoon-media.s3.ap-south-1.amazonaws.com/wa_promo_image.jpeg'}
            }
            response = requests.request(
                'POST', self.url, headers=application_json_header, data=json.dumps(payload))
            message = 'Promo message sent' if response.status_code == 200 else 'Promo message not sent'
            return message
        return 'Promo message not sent'

    def call_mark(self) -> None:
        callId = self.input.call_uuid.replace('_0', '')
        payload = {'callId': callId}
        requests.request(
            'POST', config.MARK_URL + '/flask/process', data=json.dumps(payload))

    def notify_missed_user(self, user: User, expert: Expert) -> str:
        if not user:
            return 'User not found'
        payload = {
            'template_name': 'SARATHI_MISSED_CALL' if expert.type not in non_sarathi_types else 'MISSED_INTERNAL_CALL',
            'phone_number': user.phoneNumber, 'parameters': {}
        }
        response = requests.post(self.url, json=payload)
        message = 'Missed call message sent' if response.status_code == 200 else 'Missed call message not sent'
        print(message)
        return message

    def notify_failed_expert(self, expert: Expert, user: User) -> str:
        payload = {
            'template_name': 'SARATHI_MISSED_CALL_FROM_USER_PROD',
            'phone_number': expert.phoneNumber,
            "parameters": {
                "user_name": user.name or user.phoneNumber,
                "expert_name": expert.name or expert.phoneNumber,
                "status": self.status,
                "reason": str(self.failed_reason).replace('expert ', ' ')
            }
        }
        response = requests.post(self.url, json=payload)
        message = 'Failed call message sent' if response.status_code == 200 else 'Failed call message not sent'
        print(message)
        return message

    def escalate(self, call: Call) -> str:
        url = config.URL + '/actions/escalate'
        payload = None
        if call.type == 'escalated' and call.scheduledId:
            query = {'_id': ObjectId(call.scheduledId)}
            payload = self.escalations_collection.find_one(query)
        if not payload:
            payload = {
                'user_id': str(call.user),
                'expert_id': str(call.expert),
                'escalations': []
            }
        response = requests.post(url, json=payload)
        response_dict = response.json()
        if 'output_status' in response_dict and response_dict['output_status'] == 'SUCCESS':
            message = 'Escalation successful'
        message = 'Escalation failed'
        print(message, '__call_webhook__')
        return message

    def compute(self) -> Output:
        callId = self.input.call_uuid.replace('_0', '')
        call = self.find_call(callId)
        if not call:
            return Output(
                output_status=OutputStatus.FAILURE,
                output_message=f'Call not found with callId: {callId}'
            )

        user = self.find_user(call)
        expert = self.find_expert(call)
        call_message = self.update_call(call)
        schedule_message = self.update_schedule(call)

        call = self.find_call(callId)
        expert_message = self.update_expert(call)
        user_message = self.update_user(call, expert, user)
        feedback_message = 'Feedback message not sent'

        if call.status == 'missed':
            self.notify_missed_user(user, expert)

        if call.status == 'failed':
            # self.notify_failed_expert(expert, user)
            self.escalate(call)

        feedback_message = self.send_feedback_message(call, expert, user)
        promo_message = self.send_promo_message(call, expert, user)

        threading.Thread(target=self.call_mark).start()

        message = call_message + schedule_message + \
            user_message + expert_message + feedback_message + promo_message

        print(callId + ' updated: ' + message)
        return Output(
            output_details=Common.jsonify(call.__dict__),
            output_status=OutputStatus.SUCCESS,
            output_message=message
        )
