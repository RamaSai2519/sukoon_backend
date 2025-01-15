from shared.models.interfaces import UpsertScheduleInput as Input, WhtasappMessageInput
from shared.db.users import get_meta_collection, get_user_collection
from shared.models.constants import not_interested_statuses
from shared.db.experts import get_experts_collections
from shared.models.common import Common
from datetime import datetime
from bson import ObjectId


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.meta_collection = get_meta_collection()
        self.users_collection = get_user_collection()
        self.experts_collection = get_experts_collections()

    def get_meta(self) -> dict:
        user_id = ObjectId(self.input.user_id)
        query = {'user': user_id}
        return self.meta_collection.find_one(query)

    def validate_mandatory_fields(self) -> tuple:
        mandatory_fields = ['job_time', 'job_type', 'initiatedBy',
                            'status']
        if self.input.job_type == 'WA':
            mandatory_fields.append('payload')
        elif self.input.job_type == 'CALL':
            mandatory_fields.append('user_id')
            mandatory_fields.append('expert_id')
        for field in mandatory_fields:
            if not getattr(self.input, field):
                return False, f'{field.replace('_', ' ').capitalize()} is mandatory'
        return True, ''

    def validate_job_time_and_status(self) -> tuple:
        try:
            datetime.strptime(self.input.job_time, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            return False, 'Job time is not a valid AWS time string'

        if self.input.status not in ['PENDING', 'WAPENDING']:
            return False, 'Invalid status'

        return True, ''

    def validate_user(self) -> tuple:
        user_meta = self.get_meta()
        if not user_meta:
            return True, ''

        if user_meta.get('userStatus') in not_interested_statuses:
            return False, 'User is not interested'

        return True, ''

    def validate_ids(self) -> tuple:
        try:
            ObjectId(self.input.user_id)
            ObjectId(self.input.expert_id)
        except Exception:
            return False, 'Invalid user_id or expert_id'

        return True, ''

    def validate_payload(self) -> tuple:
        try:
            WhtasappMessageInput(**self.input.payload)
        except Exception:
            return False, 'Invalid payload'

        return True, ''

    def get_req_balance(self) -> str:
        expert_id = ObjectId(self.input.expert_id)
        query = {'_id': expert_id}
        expert = self.experts_collection.find_one(query)
        req_balance = 'sarathi_calls'
        if expert.get('type') == 'expert':
            req_balance = 'expert_calls'
        return req_balance

    def validate_balance(self) -> tuple:
        req_balance = self.get_req_balance()
        if not Common.authorize_action(self.input.user_id, req_balance, 'done'):
            return False, 'Insufficient balance'

        return True, ''

    def validate_input(self) -> tuple:
        if self.input.isDeleted and self.input._id:
            return True, ''

        funcs = [self.validate_mandatory_fields,
                 self.validate_job_time_and_status]
        if self.input.job_type == 'CALL':
            funcs.append(self.validate_user)
            funcs.append(self.validate_ids)
            funcs.append(self.validate_balance)
        elif self.input.job_type == 'WA':
            funcs.append(self.validate_payload)

        for func in funcs:
            is_valid, message = func()
            if not is_valid:
                return is_valid, message

        return True, ''
