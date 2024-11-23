from bson import ObjectId
from shared.db.users import get_user_collection
from shared.models.interfaces import UpsertEngagementDataInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.collection = get_user_collection()

    def validate_input(self) -> tuple:
        if not self.is_valid_user():
            return False, "User not found"

        return True, ""

    def is_valid_user(self) -> bool:
        return self.collection.find_one({"_id": ObjectId(self.input.key)}) is not None
