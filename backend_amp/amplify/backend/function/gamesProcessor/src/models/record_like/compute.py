from shared.models.interfaces import RecordSongLikeInput as Input, Output
from shared.db.content import get_likes_collection
from shared.models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.likes_collection = get_likes_collection()

    def compute(self) -> Output:
        query = self.input.__dict__
        like = self.likes_collection.find_one(query)
        if not like:
            insertion = self.likes_collection.insert_one(query)
            query["_id"] = insertion.inserted_id
            like = query

        return Output(
            output_details=Common.jsonify(like),
            output_message="Liked song successfully"
        )
