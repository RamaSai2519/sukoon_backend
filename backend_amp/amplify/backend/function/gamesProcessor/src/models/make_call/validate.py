import requests
from bson import ObjectId
from shared.configs import CONFIG as config
from models.make_call.slack import SlackNotifier
from shared.db.experts import get_experts_collections
from shared.models.interfaces import CallInput as Input
from shared.models.constants import not_interested_statuses
from shared.db.users import get_user_collection, get_meta_collection


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.notifier = SlackNotifier()
        self.meta_collection = get_meta_collection()
        self.users_collection = get_user_collection()
        self.experts_collection = get_experts_collections()

    def get_users(self, user_id: ObjectId, expert_id: ObjectId) -> tuple:
        user = self.users_collection.find_one({'_id': user_id})
        user_meta = self.meta_collection.find_one({'user': user_id})
        expert = self.experts_collection.find_one({'_id': expert_id})

        return user, user_meta, expert

    def validate_input(self) -> tuple:
        if self.input.type_ not in ['call', 'scheduled']:
            return False, 'Invalid type'

        user, user_meta, expert = self.get_users(
            ObjectId(self.input.user_id), ObjectId(self.input.expert_id))

        user_validation = self.validate_user(user, user_meta, expert)
        if not user_validation[0]:
            return user_validation

        expert_validation = self.validate_expert(user, expert)
        if not expert_validation[0]:
            return expert_validation

        if user_validation[1]['phoneNumber'] == expert_validation[1]['phoneNumber']:
            return False, 'User and Expert phone number cannot be same'

        return True, ''

    def validate_user(self, user: dict, user_meta: dict, expert: dict) -> tuple:
        if not user:
            return False, 'User not found'

        if user.get('isActive') is False:
            return False, 'User is inactive'

        if user.get('isBusy') is True:
            self.notifier.send_notification(
                type_=self.input.type_,
                user_name=user.get('name', ''),
                sarathi_name=expert.get('name', ''),
                status='user_busy',
            )
            return False, 'User is busy'

        if user_meta and user_meta.get('userStatus') in not_interested_statuses:
            return False, 'User is not interested'

        conditions = [
            user.get('isPaidUser') is False,
            expert.get('type') != 'internal',
            user.get('numberOfCalls', 0) <= 0,
        ]

        if all(conditions):
            self.notifier.send_notification(
                type_=self.input.type_,
                user_name=user.get('name', ''),
                sarathi_name=expert.get('name', ''),
                status='balance_low',
            )
            return False, 'User has reached maximum number of calls'

        return True, user

    def notify_failed_expert(self, expert: dict, user: dict, reason: str) -> str:
        url = config.URL + '/actions/send_whatsapp'
        user_name = user.get('name', user['phoneNumber'])
        expert_name = expert.get('name', expert['phoneNumber'])
        payload = {
            'template_name': 'SARATHI_MISSED_CALL_FROM_USER_PROD',
            'phone_number': expert['phoneNumber'],
            'parameters': {
                'user_name': user_name,
                'expert_name': expert_name,
                'status': 'failed',
                'reason': reason
            }
        }
        response = requests.post(url, json=payload)
        message = 'Failed call message sent' if response.status_code == 200 else 'Failed call message not sent'
        print(message)
        return message

    def validate_expert(self, user: dict, expert: dict) -> tuple:
        if not expert:
            return False, 'Expert not found'

        if expert.get('status') == 'offline':
            self.notifier.send_notification(
                type_=self.input.type_,
                user_name=user.get('name', ''),
                sarathi_name=expert.get('name', ''),
                status='offline',
            )
            self.notify_failed_expert(expert, user, 'Offline')
            return False, 'Expert is offline'

        if expert.get('isBusy') is True:
            self.notifier.send_notification(
                type_=self.input.type_,
                user_name=user.get('name', ''),
                sarathi_name=expert.get('name', ''),
                status='sarathi_busy',
            )
            self.notify_failed_expert(expert, user, 'Busy')
            return False, 'Expert is busy'

        return True, expert
