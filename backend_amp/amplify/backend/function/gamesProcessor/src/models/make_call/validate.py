import requests
from bson import ObjectId
from datetime import timedelta
from shared.models.common import Common
from shared.configs import CONFIG as config
from models.make_call.slack import SlackNotifier
from shared.db.experts import get_experts_collections
from shared.models.interfaces import CallInput as Input
from shared.db.schedules import get_schedules_collection
from shared.db.users import get_user_collection, get_meta_collection
from shared.db.calls import get_escalations_collection, get_calls_collection
from shared.models.constants import not_interested_statuses, non_sarathi_types


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.notifier = SlackNotifier()
        self.meta_collection = get_meta_collection()
        self.users_collection = get_user_collection()
        self.calls_collection = get_calls_collection()
        self.experts_collection = get_experts_collections()
        self.schedules_collection = get_schedules_collection()
        self.escalations_collection = get_escalations_collection()

    def get_users(self, user_id: ObjectId, expert_id: ObjectId) -> tuple:
        user = self.users_collection.find_one({'_id': user_id})
        user_meta = self.meta_collection.find_one({'user': user_id})
        expert = self.experts_collection.find_one({'_id': expert_id})

        return user, user_meta, expert

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
                'status': 'missed',
                'reason': reason
            }
        }
        response = requests.post(url, json=payload)
        if 'output_status' in response.json() and response.json()['output_status'] == 'SUCCESS':
            message = 'Failed call message sent to expert'
        message = 'Failed call message not sent to expert'
        print(message, '__make_call__')

        # Notify missed user
        if expert.get('type') == 'saarthi' and self.input.scheduledId not in [None, '']:
            payload = {
                'template_name': 'SARATHI_FAILED_CALL_TO_USER',
                'phone_number': user['phoneNumber'],
                'parameters': {}
            }
            response = requests.post(url, json=payload)
            if 'output_status' in response.json() and response.json()['output_status'] == 'SUCCESS':
                message = 'Failed call message sent to user'
            message = 'Failed call message not sent to user'
            print(message, '__make_call__')
        return message

    def escalate(self) -> str:
        url = config.URL + '/actions/escalate'
        payload = None
        if self.input.type_ == 'escalated' and self.input.scheduledId:
            query = {'_id': ObjectId(self.input.scheduledId)}
            payload = self.escalations_collection.find_one(query)
        if not payload:
            payload = {
                'user_id': self.input.user_id,
                'expert_id': self.input.expert_id,
                'escalations': []
            }
        payload = Common.jsonify(payload)
        response = requests.post(url, json=payload)
        if 'output_status' in response.json() and response.json()['output_status'] == 'SUCCESS':
            message = 'Escalation successful'
        message = 'Escalation failed'
        print(message, '__make_call__')
        print('user_id: ', self.input.user_id,
              'expert_id: ', self.input.expert_id)
        return message

    def check_user_availability(self, user: dict) -> bool:
        lower_bound = Common.get_current_utc_time() + timedelta(minutes=1)
        upper_bound = lower_bound + timedelta(minutes=10)
        query = {
            'job_time': {'$gte': lower_bound, '$lte': upper_bound},
            "isDeleted": {"$ne": True},
            'user_id': user['_id'],
        }
        schedule = self.schedules_collection.find_one(query)
        return False if schedule else True

    def check_expert_availability(self, expert: dict) -> bool:
        lower_bound = Common.get_current_utc_time() + timedelta(minutes=1)
        upper_bound = lower_bound + timedelta(minutes=10)
        query = {
            'job_time': {'$gte': lower_bound, '$lte': upper_bound},
            "isDeleted": {"$ne": True},
            'expert_id': expert['_id'],
        }
        schedule = self.schedules_collection.find_one(query)
        return False if schedule else True

    def validate_expert(self, user: dict, expert: dict) -> tuple:
        if not expert:
            return False, 'Expert not found'

        if self.check_expert_availability(expert) is False:
            return False, 'Expert has an upcoming call'

        if expert.get('status') == 'offline':
            self.notifier.send_notification(
                type_=self.input.type_,
                user_name=user.get('name', ''),
                sarathi_name=expert.get('name', ''),
                status='offline',
            )
            self.notify_failed_expert(expert, user, 'Offline')
            if expert.get('type') == 'saarthi' and self.input.scheduledId not in [None, '']:
                self.escalate()
            return False, 'Expert is offline'

        if expert.get('isBusy') is True:
            self.notifier.send_notification(
                type_=self.input.type_,
                user_name=user.get('name', ''),
                sarathi_name=expert.get('name', ''),
                status='sarathi_busy',
            )
            self.notify_failed_expert(expert, user, 'on another call')
            return False, 'Expert is busy'

        # if self.input.type_ == 'call':
        #     req_balance = 'sarathi_calls'
        #     if expert.get('type', 'sarathi') == 'expert':
        #         req_balance = 'expert_calls'
        #     if not Common.authorize_action(str(user['_id']), req_balance, 'done'):
        #         return False, 'Invalid Token'

        return True, expert

    def check_user_previous_call(self, user: dict) -> bool:
        lower_bound = Common.get_current_utc_time() - timedelta(minutes=5)
        upper_bound = Common.get_current_utc_time()
        query = {
            'user': user['_id'],
            'direction': {'$ne': 'inbound'},
            'initiatedTime': {'$gte': lower_bound, '$lte': upper_bound}
        }
        call = self.calls_collection.find_one(query)
        return False if call else True

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

        if self.check_user_availability(user) is False:
            return False, 'User has an upcoming call'

        if self.check_user_previous_call(user) is False:
            return False, 'User had a recent call'

        return True, user

    def validate_input(self) -> tuple:
        if self.input.type_ not in ['call', 'scheduled', 'escalated']:
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

        query = {'status': {
            '$nin': ['missed', 'successful', 'inadequate', 'failed']}}
        calls = self.calls_collection.count_documents(query)
        if calls >= 5:
            return False, 'Maximum call limit reached'

        return True, ''
