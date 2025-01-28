import bcrypt
from shared.models.common import Common
from shared.db.referral import get_ad_clicks_collection
from shared.models.interfaces import RecordAdClickInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_ad_clicks_collection()

    def validate_token(self) -> dict:
        query = {'token': self.input.token}
        doc = self.collection.find_one(query)
        return doc if doc else False

    def generate_token(self, uid: str) -> str:
        token = bcrypt.hashpw(uid.encode("utf-8"), bcrypt.gensalt())
        return token.decode("utf-8")

    def prep_doc(self, new: bool = True) -> dict:
        doc = self.input.__dict__
        doc.pop('token')
        doc = Common.filter_none_values(doc)
        if new:
            doc['createdAt'] = Common.get_current_utc_time()
        else:
            doc['updatedAt'] = Common.get_current_utc_time()
        return doc

    def compute(self) -> Output:
        doc = self.validate_token()
        if not doc:
            doc = self.prep_doc()
            inserted_id = self.collection.insert_one(doc).inserted_id
            doc['token'] = self.generate_token(str(inserted_id))
            self.collection.update_one({'_id': inserted_id}, {'$set': doc})
        else:
            query = {'_id': doc['_id']}
            doc = self.prep_doc(False)
            self.collection.update_one(query, {'$set': doc})

        return Output(
            output_details=Common.jsonify(doc),
            output_message='Recorded Click'
        )
