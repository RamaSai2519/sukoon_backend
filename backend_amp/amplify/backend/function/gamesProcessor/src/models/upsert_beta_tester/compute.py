from shared.models.common import Common
from shared.db.misc import get_beta_testers_collection
from shared.models.interfaces import UpsertBetaTesterInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_beta_testers_collection()

    def compute(self) -> Output:
        upsertion = self.collection.find_one_and_update(
            {"phoneNumber": self.input.phoneNumber},
            {"$set": self.input.__dict__},
            upsert=True,
            return_document=True
        )

        return Output(
            output_message="Beta Tester upserted successfully",
            output_details=Common.jsonify(upsertion)
        )
