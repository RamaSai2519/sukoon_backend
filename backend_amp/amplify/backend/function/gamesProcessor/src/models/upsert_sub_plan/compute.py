from shared.models.common import Common
from shared.db.users import get_subscription_plans_collection
from shared.models.interfaces import UpsertSubPlanInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_subscription_plans_collection()

    def compute(self) -> Output:
        query = {'name': self.input.name}
        doc = self.collection.find_one_and_update(
            query,
            {'$set': self.input.__dict__},
            upsert=True,
            return_document=True
        )

        return Output(
            output_details=Common.jsonify(doc),
            output_message="Successfully upserted subscription plan"
        )
