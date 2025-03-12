from shared.models.interfaces import Escalation as Input, Output, EachEscalation
from shared.db.calls import get_escalations_collection
from shared.db.experts import get_experts_collections
from shared.models.constants import OutputStatus
from shared.configs import CONFIG as config
from shared.models.common import Common
from dataclasses import asdict
from bson import ObjectId
import requests


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.expert_number = None
        self.collection = get_escalations_collection()
        self.experts_collection = get_experts_collections()

    def get_expert_id_by_level(self, level: int) -> str:
        query = {'escalation_level': level}
        query['status'] = 'online'
        while True:
            expert = self.experts_collection.find_one(query)
            if expert:
                self.expert_number = expert['phoneNumber']
                return expert['_id']
            else:
                level += 1
                query['escalation_level'] = level
                if level > 5:
                    return None

    def prep_data(self, doc: dict) -> dict:
        object_id_fields = ['_id', 'user_id', 'expert_id']
        for field in object_id_fields:
            if field in doc and isinstance(doc[field], str):
                doc[field] = ObjectId(doc[field])

        escalations = doc.get('escalations', [])
        for each in escalations:
            if isinstance(each.get('expert_id'), str):
                each['expert_id'] = ObjectId(each['expert_id'])
        doc['escalations'] = escalations

        doc['updated_at'] = Common.get_current_utc_time()
        doc = Common.filter_none_values(doc)
        return doc

    def get_doc(self) -> dict:
        query = {"_id": ObjectId(self.input._id)}
        doc = self.collection.find_one(query)
        return doc if doc else None

    def create_escaltion(self) -> dict:
        doc = asdict(self.input)
        doc['escalations'] = []
        doc = self.prep_data(doc)
        doc['created_at'] = Common.get_current_utc_time()
        inserted_id = self.collection.insert_one(doc).inserted_id
        self.input._id = str(inserted_id)
        return doc

    def make_call(self, expert_id: str) -> requests.Response:
        url = config.URL + '/actions/call'
        payload = {
            'type_': 'escalated',
            'expert_id': expert_id,
            'scheduledId': str(self.input._id),
            'user_id': str(self.input.user_id),
            'user_requested': False
        }

        balance = self.common.get_balance_type(expert_id)
        token = Common.get_token(str(self.input.user_id), balance)
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.post(url, json=payload, headers=headers)
        print(response.text)

        return response

    def notify_agent(self) -> None:
        url = config.URL + '/actions/send_whatsapp'
        payload = {
            'phone_number': self.expert_number,
            'template_name': 'ESCALATION_MESSAGE_PROD',
            'parameters': {
                'misc': str(self.input.user_id)
            }
        }
        response = requests.post(url, json=payload)
        print('Agent notified' if response.status_code ==
              200 else 'Agent not notified')

    def compute(self) -> Output:
        if not self.input._id:
            doc = self.create_escaltion()
        doc = self.get_doc()
        if doc.get('escalations', []) == []:
            current_level = 0
        else:
            current_level = doc['escalations'][-1]['level']
        if current_level > 5:
            return Output(output_message="Escalation already at highest level", output_status=OutputStatus.FAILURE)

        new_level = current_level + 1
        expert_id = self.get_expert_id_by_level(new_level)
        if not expert_id:
            return Output(
                output_message="No expert available for escalation", output_status=OutputStatus.FAILURE
            )

        new_escalation = EachEscalation(
            level=new_level, expert_id=expert_id,
            time=Common.get_current_utc_time()
        ).__dict__
        doc['escalations'].append(new_escalation)
        doc = self.prep_data(doc)
        self.collection.update_one(
            {"_id": ObjectId(self.input._id)},
            {"$set": doc}
        )
        self.make_call(str(expert_id))

        return Output(
            output_message="Escalated successfully"
        )
