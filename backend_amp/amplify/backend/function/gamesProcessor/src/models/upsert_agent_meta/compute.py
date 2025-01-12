from bson import ObjectId
from dataclasses import asdict
from shared.models.common import Common
from shared.db.experts import get_agents_meta_collection
from shared.models.interfaces import UpsertAgentMetaInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_agents_meta_collection()

    def compute(self) -> Output:
        data = asdict(self.input)
        data['agent_id'] = ObjectId(data['agent_id'])
        data['updatedAt'] = Common.get_current_utc_time()
        upsertion = self.collection.update_one(
            {"agent_id": data["agent_id"]},
            {"$set": data},
            upsert=True
        )

        return Output(output_message="Agent meta data upserted successfully")
