from bson import ObjectId
from models.make_call.slack import SlackNotifier
from shared.db.experts import get_experts_collections
from shared.models.interfaces import CallInput as Input
from shared.models.constants import not_interested_statuses
from shared.db.users import get_user_collection, get_meta_collection


class Validator:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.notifier = SlackNotifier()
        self.meta_collection = get_meta_collection()
        self.users_collection = get_user_collection()
        self.experts_collection = get_experts_collections()

    def get_users(self, user_id: ObjectId, expert_id: ObjectId) -> tuple:
        user = self.users_collection.find_one({"_id": user_id})
        user_meta = self.meta_collection.find_one({"user": user_id})
        expert = self.experts_collection.find_one({"_id": expert_id})

        return user, user_meta, expert

    def validate_input(self):
        if self.input.type_ not in ["call", "scheduled"]:
            return False, "Invalid type"

        user, user_meta, expert = self.get_users(
            ObjectId(self.input.user_id), ObjectId(self.input.expert_id))

        user_validation = self.validate_user(user, user_meta, expert)
        if not user_validation[0]:
            return user_validation

        expert_validation = self.validate_expert(user, expert)
        if not expert_validation[0]:
            return expert_validation

        if user_validation[1]["phoneNumber"] == expert_validation[1]["phoneNumber"]:
            return False, "User and Expert phone number cannot be same"

        return True, ""

    def validate_user(self, user: dict, user_meta: dict, expert: dict) -> tuple:
        if not user:
            return False, "User not found"

        if user["active"] is False:
            return False, "User is inactive"

        if user["isBusy"]:
            self.notifier.send_notification(
                type_=self.input.type_,
                user_name=user.get("name", ""),
                sarathi_name=expert.get("name", ""),
                status="user_busy",
            )
            return False, "User is busy"

        if user_meta and user_meta.get("userStatus") in not_interested_statuses:
            return False, "User is not interested"

        conditions = [
            user.get("isPaidUser") is False,
            expert.get("type") != "internal",
            user.get("numberOfCalls", 0) <= 0,
        ]

        if all(conditions):
            self.notifier.send_notification(
                type_=self.input.type_,
                user_name=user.get("name", ""),
                sarathi_name=expert.get("name", ""),
                status="balance_low",
            )
            return False, "User has reached maximum number of calls"

        return True, user

    def validate_expert(self, user: dict, expert: dict) -> tuple:
        if not expert:
            return False, "Expert not found"

        if expert["status"] == "offline":
            self.notifier.send_notification(
                type_=self.input.type_,
                user_name=user.get("name", ""),
                sarathi_name=expert.get("name", ""),
                status="offline",
            )
            return False, "Expert is offline"

        if expert["isBusy"]:
            self.notifier.send_notification(
                type_=self.input.type_,
                user_name=user.get("name", ""),
                sarathi_name=expert.get("name", ""),
                status="sarathi_busy",
            )
            return False, "Expert is busy"

        return True, expert
