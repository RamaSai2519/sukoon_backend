from shared.models.common import Common
from shared.db.whatsapp import get_wa_refs_collection
from shared.models.interfaces import UpsertWaRefInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_wa_refs_collection()

    def get_ref(self) -> dict:
        query = {'source': self.input.source}
        ref = self.collection.find_one(query)
        return ref if ref else None

    def compute(self) -> Output:
        ref = self.get_ref()
        if ref:
            update = {'$set': {'message': self.input.message}}
            self.collection.update_one({'_id': ref['_id']}, update)
            message = f"Updated message for source: {self.input.source}"
        else:
            ref = {
                'source': self.input.source,
                'message': self.input.message
            }
            self.collection.insert_one(ref)
            message = f"Inserted message for source: {self.input.source}"

        return Output(
            output_details=Common.jsonify(ref),
            output_message=message
        )
