import hashlib
import dataclasses
from typing import Union
from datetime import datetime
from models.common import Common
from db.users import get_user_collection
from models.constants import OutputStatus
from models.interfaces import User as Input, Output
from db.referral import get_user_referral_collection


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()
        self.referrals_collection = get_user_referral_collection()

    def defaults(self, user_data: dict) -> dict:
        user_data["active"] = False
        user_data["isBusy"] = False
        user_data["isBlocked"] = False
        user_data["isPaidUser"] = False
        user_data["wa_opt_out"] = False
        user_data["numberOfGames"] = 0
        user_data["numberOfCalls"] = 3
        return user_data

    def prep_data(self, user_data: dict, new_user=True, prev_user: dict = None) -> dict:
        fields = ["birthDate", "city", "name"]
        data = {}
        for field in fields:
            data[field] = user_data.get(field) or (
                prev_user and prev_user.get(field)) or None

        user_data.pop("_id", None)
        user_data.pop("referral_code", None)
        user_data["profileCompleted"] = bool(
            data.get("name") and data.get("city") and data.get("birthDate"))

        if new_user:
            user_data = self.defaults(user_data)
            if user_data.get("profileCompleted") == True:
                user_data["referralCode"] = self.generate_referral_code(
                    data["name"], user_data["phoneNumber"])
        else:
            user_data.pop("createdDate", None)

        if isinstance(data["birthDate"], str):
            user_data["birthDate"] = Common.string_to_date(data, "birthDate")

        user_data = {k: v for k, v in user_data.items() if v is not None}
        return user_data

    def generate_referral_code(self, name: str, phone_number: str) -> str:
        raw_data = name + phone_number
        hash_object = hashlib.sha256(raw_data.encode())
        code = hash_object.hexdigest()[:8].upper()
        valid_code = self.validate_referral_code(code)
        return code if not valid_code else self.generate_referral_code(name, phone_number)

    def validate_referral_code(self, referral_code: str) -> Union[bool, dict]:
        user = self.users_collection.find_one({"referralCode": referral_code})
        return user if user else False

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
            if self.input.referral_code:
                referrer = self.validate_referral_code(
                    user_data["referralCode"])
                if referrer:
                    user_data["referredBy"] = referrer["referralCode"]
                    self.referrals_collection.insert_one(
                        {
                            "userId": referrer["_id"],
                            "referredUserId": user_data["_id"],
                            "createdAt": datetime.now(),
                        }
                    )
            user_data["_id"] = self.users_collection.insert_one(user_data)

            message = "Successfully created user"

        return Output(
            output_details=Common.jsonify(user_data),
            output_status=OutputStatus.SUCCESS,
            output_message=message
        )
