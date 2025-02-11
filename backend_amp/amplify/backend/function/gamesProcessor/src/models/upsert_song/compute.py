from bson import ObjectId
from shared.models.common import Common
from shared.db.content import get_songs_collection
from shared.models.interfaces import UpsertSongInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_songs_collection()

    def compute(self) -> Output:
        if self.input._id:
            doc = self.input.__dict__
            doc['user_id'] = ObjectId(doc['user_id'])
            doc.pop('_id')
            query = {"_id": ObjectId(self.input._id)}
            doc = self.collection.find_one_and_update(
                query, {"$set": doc},
                upsert=True, return_document=True
            )
        else:
            doc = self.input.__dict__
            doc['user_id'] = ObjectId(doc['user_id'])
            doc.pop('_id')
            insertion = self.collection.insert_one(doc)
            doc['_id'] = insertion.inserted_id

        return Output(
            output_details=Common.jsonify(doc),
            output_message="Successfully upserted song"
        )
