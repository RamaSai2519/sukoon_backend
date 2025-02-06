from shared.models.interfaces import SCallEndWebhookInput as Input, Call
from shared.db.experts import get_experts_collections
from shared.db.users import get_user_collection
from shared.models.common import Common
from bson import ObjectId


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()
        self.experts_collection = get_experts_collections()

    def find_call(self) -> Call:
        query = {'callId': self.input.call_id}
        call = self.users_collection.find_one(query)
        call = Common.clean_dict(call, Call)
        return Call(**call)

    def update_user(self, user_id: ObjectId) -> None:
        query = {'_id': user_id}
        update = {'$set': {'isBusy': False}}
        self.users_collection.update_one(query, update)

    def update_expert(self, expert_id: ObjectId) -> None:
        query = {'_id': expert_id}
        update = {'$set': {'isBusy': False}}
        self.experts_collection.update_one(query, update)

    def validate_input(self) -> tuple:
        call = {}
        try:
            call = self.find_call()
        except Exception as e:
            return False, str(e)

        self.update_user(call.user)
        self.update_expert(call.expert)

        return True, ""
