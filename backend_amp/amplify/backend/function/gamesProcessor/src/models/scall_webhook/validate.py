from shared.models.interfaces import SCallEndWebhookInput as Input, Call
from shared.db.experts import get_experts_collections
from shared.db.calls import get_calls_collection
from shared.db.users import get_user_collection
from shared.models.common import Common
from bson import ObjectId


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()
        self.calls_collection = get_calls_collection()
        self.experts_collection = get_experts_collections()

    def find_call(self) -> Call:
        query = {'_id': ObjectId(self.input.suid)}
        call = self.calls_collection.find_one(query)
        call = Common.clean_dict(call, Call)
        return Call(**call) if call else None

    def update_user(self, user_id: ObjectId) -> None:
        query = {'_id': user_id}
        update = {'$set': {'isBusy': False}}
        self.users_collection.update_one(query, update)

    def update_expert(self, expert_id: ObjectId) -> None:
        query = {'_id': expert_id}
        expert = self.experts_collection.find_one(query)
        number = expert.get('phoneNumber')
        Common.update_expert_isbusy(number, False)

    def validate_input(self) -> tuple:
        if not self.input.suid:
            return True, ""
        call = self.find_call()
        if not call:
            return False, "Call not found"

        self.update_user(call.user)
        self.update_expert(call.expert)

        return True, ""
