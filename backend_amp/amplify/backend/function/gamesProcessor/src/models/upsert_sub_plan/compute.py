from shared.models.common import Common
from shared.models.constants import user_balance_types
from shared.db.users import get_subscription_plans_collection
from shared.models.interfaces import UpsertSubPlanInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_subscription_plans_collection()

    def compute(self) -> Output:
        query = {'name': self.input.name}
        doc = self.input.__dict__
        for field in user_balance_types:
            if field in doc and not isinstance(doc[field], int):
                doc[field] = int(doc[field])

        if "price" in doc and not isinstance(doc["price"], str):
            doc["price"] = str(doc["price"])

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
