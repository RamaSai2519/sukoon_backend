import requests
from shared.models.common import Common
from shared.configs import CONFIG as config
from shared.db.calls import get_calls_collection
from shared.db.experts import get_experts_collections
from shared.models.constants import customer_care_number
from shared.models.interfaces import SCallInhookInput as Input, Call, Output, User, Expert


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.callId = self.input.uuid
        self.collection = get_calls_collection()
        self.user_number = self.input.caller_id_number
        self.experts_collection = get_experts_collections()

    def find_user(self) -> User:
        url = config.URL + '/actions/user'
        payload = {'phoneNumber': self.user_number}
        response = requests.post(url, json=payload)
        output = response.json()
        user = output.get('output_details', {})
        user = Common.clean_dict(user, User)
        user = User(**user)
        return user

    def find_expert(self) -> Expert:
        query = {'phoneNumber': customer_care_number}
        expert = self.experts_collection.find_one(query)
        expert = Common.clean_dict(expert, Expert)
        expert = Expert(**expert)
        return expert

    def compute(self) -> Output:
        user = self.find_user()
        expert = self.find_expert()
        call = Call(
            callId=self.callId,
            user=user._id,
            expert=expert._id,
            initiatedTime=Common.get_current_utc_time(),
            status='initiated',
            direction='inbound',
            type='call',
        ).__dict__
        call = Common.filter_none_values(call)
        self.collection.insert_one(call)

        return Output(output_message="Call Noted")
