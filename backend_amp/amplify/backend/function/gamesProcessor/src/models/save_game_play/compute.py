from shared.models.interfaces import Output, SaveGamePlayInput as Input
from shared.db.games import get_game_saves_collection
from shared.models.common import Common
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.saves_collection = get_game_saves_collection()

    def compute(self) -> Output:
        doc = self.input.__dict__
        doc['user_id'] = ObjectId(doc['user_id'])
        insertion = self.saves_collection.insert_one(doc)
        doc['_id'] = insertion.inserted_id

        return Output(
            output_details=Common.jsonify(doc),
            output_message="Game saved successfully"
        )
