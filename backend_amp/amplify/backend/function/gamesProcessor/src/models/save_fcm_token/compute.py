from shared.models.interfaces import SaveFCMTokenInput as Input, Output
from shared.db.admins import get_fcm_token_collection
from shared.models.constants import OutputStatus
from shared.models.common import Common
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.user_id = ObjectId(Common.get_identity())
        self.fcm_tokens_collection = get_fcm_token_collection()

    def validate_token(self) -> bool:
        query = {"token": self.input.token}
        prev_token = self.fcm_tokens_collection.find_one(query)
        return True if prev_token else False

    def update_admin(self) -> None:
        filter = {"token": self.input.token}
        update = {"$set": {"lastModifiedBy": self.user_id}}
        self.fcm_tokens_collection.update_one(filter, update)

    def save_token(self) -> None:
        document = {
            "token": self.input.token,
            "lastModifiedBy": self.user_id
        }
        self.fcm_tokens_collection.insert_one(document)

    def compute(self) -> Output:
        prev_token = self.validate_token()
        if prev_token:
            self.update_admin()
            message = "Token already exists"
        else:
            self.save_token()
            message = "Token saved successfully"

        return Output(
            output_details="",
            output_status=OutputStatus.SUCCESS,
            output_message=message
        )
