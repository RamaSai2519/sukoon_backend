from shared.models.interfaces import GetAgentsMetaInput as Input, Output
from shared.db.experts import get_agents_meta_collection
from shared.models.common import Common
from bson import ObjectId
import json


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_agents_meta_collection()

    def compute(self) -> Output:
        query = Common.get_filter_query(
            self.input.filter_field, self.input.filter_value)
        objectid_fields = ['_id', 'agent_id']
        if self.input.filter_field in objectid_fields:
            query[self.input.filter_field] = ObjectId(self.input.filter_value)

        if self.input.filter_field == 'call_meta':
            query['call_meta'] = json.loads(self.input.filter_value)

        cursor = self.collection.find(query).sort('updatedAt', -1)
        cursor = Common.paginate_cursor(cursor, int(
            self.input.page), int(self.input.size))
        agents_meta = list(cursor)
        total = self.collection.count_documents(query)

        return Output(
            output_details={
                'data': Common.jsonify(agents_meta),
                'total': total
            },
            output_message="Agents meta data fetched successfully"
        )
