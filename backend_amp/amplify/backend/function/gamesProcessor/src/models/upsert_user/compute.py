import dataclasses
from typing import Union
from bson import ObjectId
from datetime import datetime
from models.common import Common
from db.users import get_user_collection
from models.constants import OutputStatus
from models.interfaces import User as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()

    def prep_data(self, user_data: dict, new_user=True, prev_user: dict = None) -> dict:
        fields = ["birthDate", "city", "name"]
        data = {}
        for field in fields:
            data[field] = user_data.get(field) or (
                prev_user and prev_user.get(field)) or None
        if new_user:
            user_data["active"] = True
            user_data["isBusy"] = False
            user_data["isBlocked"] = False
            user_data["isPaidUser"] = False
            user_data["wa_opt_out"] = False
            user_data["numberOfGames"] = 0
            user_data["numberOfCalls"] = 3

        if not new_user:
            user_data.pop("createdDate", None)

        user_data.pop("_id", None)
        user_data["profileCompleted"] = bool(
            data.get("name") and data.get("city") and data.get("birthDate"))

        user_data = {k: v for k, v in user_data.items() if v is not None}
        return user_data

    def validate_phoneNumber(self, phoneNumber: str) -> Union[bool, dict]:
        user = self.users_collection.find_one({"phoneNumber": phoneNumber})
        return user if user else False

    def compute(self) -> Output:
        user = self.input
        user_data = dataclasses.asdict(user)
        prev_user = self.validate_phoneNumber(user_data["phoneNumber"])

        if prev_user:
            user_data = self.prep_data(user_data, False, prev_user)
            self.users_collection.update_one(
                {"phoneNumber": user_data["phoneNumber"]},
                {"$set": user_data}
            )
            message = "Successfully updated user"
        else:
            user_data = self.prep_data(user_data)
            self.users_collection.insert_one(user_data)
            message = "Successfully created user"

        return Output(
            output_details=Common.jsonify(user_data),
            output_status=OutputStatus.SUCCESS,
            output_message=message
        )
