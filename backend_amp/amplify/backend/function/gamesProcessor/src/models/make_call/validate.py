from bson import ObjectId
from db.users import get_user_collection
from db.experts import get_experts_collections
from models.interfaces import CallInput as Input


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()
        self.experts_collection = get_experts_collections()

    def validate_input(self) -> tuple[bool, str]:
        if not self.input.user_id:
            return False, "user_id is required"

        if not self.input.expert_id:
            return False, "expert_id is required"

        user_validation = self.validate_user()
        if not user_validation[0]:
            return user_validation

        expert_validation = self.validate_expert()
        if not expert_validation[0]:
            return expert_validation

        if user_validation[1]["phoneNumber"] == expert_validation[1]["phoneNumber"]:
            return False, "User and Expert phone number cannot be same"

        return True, ""

    def validate_user(self) -> tuple[bool, dict | str]:
        user = self.users_collection.find_one(
            {"_id": ObjectId(self.input.user_id)})

        if not user:
            return False, "User not found"

        if user["isBusy"]:
            return False, "User is busy"

        if user["numberOfCalls"] <= 0:
            return False, "User has reached maximum number of calls"

        return True, user

    def validate_expert(self) -> tuple[bool, dict | str]:
        expert = self.experts_collection.find_one(
            {"_id": ObjectId(self.input.expert_id)})
            
        if not expert:
            return False, "Expert not found"

        if expert["status"] == "offline":
            return False, "Expert is offline"

        if expert["isBusy"]:
            return False, "Expert is busy"

        return True, expert
