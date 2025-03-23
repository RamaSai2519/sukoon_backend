from shared.models.interfaces import UpdateFCMTokenInput as Input, Output
from shared.db.users import get_user_fcm_token_collection
from shared.models.common import Common
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_user_fcm_token_collection()

    def get_stored_doc(self, user_id: ObjectId) -> dict:
        query = {"user": user_id}
        return self.collection.find_one(query)

    def update_doc(self, doc: dict) -> dict:
        if self.input.fcm_token in [token['token'] for token in doc['tokens']]:
            return doc
        if len(doc['tokens']) >= 5:
            doc['tokens'].pop(0)
        doc['tokens'].append({
            'token': self.input.fcm_token,
            'createdAt': Common.get_current_utc_time()
        })
        return doc

    def compute(self) -> Output:
        user_id = ObjectId(self.input.user_id)
        doc = self.get_stored_doc(user_id)
        if not doc:
            doc = {
                'user': user_id,
                'tokens': [],
                'createdAt': Common.get_current_utc_time()
            }

        doc = self.update_doc(doc)
        self.collection.replace_one({"user": user_id}, doc, upsert=True)

        return Output(output_message="Successfully updated FCM token")
