from shared.models.interfaces import UpsertRefTokenInput as Input, Output
from shared.db.referral import get_ref_tokens_collection
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.ref_tokens_collection = get_ref_tokens_collection()

    def compute(self) -> Output:
        query = {'name': self.input.name}
        upsert = self.ref_tokens_collection.find_one_and_update(
            query,
            {"$set": self.input.__dict__},
            upsert=True,
            return_document=True
        )

        return Output(
            output_details=Common.jsonify(upsert),
            output_message="Referral Token Upserted",
        )
