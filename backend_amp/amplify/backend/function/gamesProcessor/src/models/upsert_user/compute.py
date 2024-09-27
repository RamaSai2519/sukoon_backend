import json
import string
import random
import hashlib
import requests
import dataclasses
from typing import Union
from datetime import datetime
from models.common import Common
from db.users import get_user_collection
from models.constants import OutputStatus, application_json_header
from models.interfaces import User as Input, Output
from db.referral import get_user_referral_collection


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()
        self.referrals_collection = get_user_referral_collection()

    def defaults(self, user_data: dict) -> dict:
        user_data["active"] = True
        user_data["isBusy"] = False
        user_data["isBlocked"] = False
        user_data["isPaidUser"] = False
        user_data["wa_opt_out"] = False
        user_data["numberOfGames"] = 0
        user_data["numberOfCalls"] = 3
        user_data.pop("_id", None)
        return user_data

    def merge_old_data(self, user_data: dict, prev_user: dict) -> dict:
        for key, value in prev_user.items():
            if key not in user_data or user_data[key] is None or user_data[key] == "":
                user_data[key] = value
        return user_data

    def pop_immutable_fields(self, user_data: dict) -> dict:
        fields = ["_id", "phoneNumber", "refCode", "createdDate"]
        for field in fields:
            user_data.pop(field, None)
        return user_data

    def prep_data(self, user_data: dict, prev_user: dict = None) -> dict:
        # Merge old data if user already exists or set defaults
        if prev_user:
            user_data = self.pop_immutable_fields(user_data)
            user_data = self.merge_old_data(user_data, prev_user)
        else:
            user_data = self.defaults(user_data)
        user_data.pop("refCode", None)

        # Check if profile is completed
        user_data["profileCompleted"] = bool(
            user_data.get("name") and user_data.get("city") and user_data.get("birthDate"))

        # Generate referral code if profile is completed and If there is no prev_user, or if there is one but without a refCode
        if user_data.get("profileCompleted") and (not prev_user or not prev_user.get("refCode")):
            user_data["refCode"] = self.generate_referral_code(
                user_data["name"], user_data["phoneNumber"])

        # Convert birthDate to datetime object
        if isinstance(user_data.get("birthDate"), str):
            user_data["birthDate"] = Common.string_to_date(
                user_data, "birthDate")

        # Remove None values
        user_data = {k: v for k, v in user_data.items() if v is not None}
        return user_data

    def send_welcome_message(self, user_data: dict) -> None:
        url = "https://6x4j0qxbmk.execute-api.ap-south-1.amazonaws.com/main/actions/send_whatsapp"
        # url = "http://localhost:8080/actions/send_whatsapp"
        headers = {
            'Content-Type': 'application/json'
        }
        payload = {"template_name": "WELCOME_REGISTRATION",
                   "phone_number": user_data.get("phoneNumber", ""),
                   "parameters": {
                       "user_name": user_data.get("name", "")
                   }}
        response = requests.request(
            "POST", url, headers=headers, data=json.dumps(payload)
        )

        if response.status_code != 200:
            print(response.text)
        return True if response.status_code == 200 else False

    def generate_referral_code(self, name: str, phone_number: str) -> str:
        salt = ''.join(random.choices(string.ascii_letters, k=6))
        raw_data = name + phone_number + salt
        hash_object = hashlib.sha256(raw_data.encode())
        code = hash_object.hexdigest()[:8].upper()
        valid_code = self.validate_referral_code(code)
        return code if not valid_code else self.generate_referral_code(name, phone_number)

    def validate_referral_code(self, referral_code: str) -> Union[bool, dict]:
        user = self.users_collection.find_one({"refCode": referral_code})
        return user if user else False

    def validate_phoneNumber(self, phoneNumber: str) -> Union[dict, None]:
        user = self.users_collection.find_one({"phoneNumber": phoneNumber})
        return user if user else None

    def validate_referral(self, referred_user_id: str) -> bool:
        filter = {"referredUserId": referred_user_id}
        referral = self.referrals_collection.find_one(filter)
        return True if referral else False

    def insert_referral(self, referred_user_id: str, user_id: str) -> None:
        referral = {
            "referredUserId": referred_user_id,  # Referred User
            "userId": user_id,  # Referrer
        }
        if not self.validate_referral(referred_user_id):
            referral["createdAt"] = datetime.now()
            self.referrals_collection.insert_one(referral)

    def update_user(self, user_data: dict, prev_user: dict) -> str:
        self.users_collection.update_one(
            {"phoneNumber": user_data["phoneNumber"]},
            {"$set": user_data}
        )
        return "Successfully updated user"

    def insert_user(self, user_data: dict) -> str:
        user_data["_id"] = self.users_collection.insert_one(
            user_data).inserted_id
        return "Successfully created user", user_data

    def handle_referral(self, user_data: dict, prev_user: dict) -> str:
        if self.input.refCode:
            referrer = self.validate_referral_code(self.input.refCode)
            if referrer and not user_data.get("refSource"):
                self.insert_referral(user_data["_id"], referrer["_id"])
            else:
                if not self.validate_referral(user_data["_id"]) and (not prev_user or not prev_user.get("refSource")):
                    user_data["refSource"] = self.input.refCode
        self.update_user(user_data, prev_user)

    def compute(self) -> Output:
        user = self.input
        user_data = dataclasses.asdict(user)
        prev_user = self.validate_phoneNumber(user_data["phoneNumber"])

        user_data = self.prep_data(user_data, prev_user)
        if prev_user:
            message = self.update_user(user_data, prev_user)
        else:
            message, user_data = self.insert_user(user_data)
            response = self.send_welcome_message(user_data)
            message += " and sent welcome message" if response else " but failed to send welcome message"
        self.handle_referral(user_data, prev_user)

        return Output(
            output_details=Common.jsonify(user_data),
            output_status=OutputStatus.SUCCESS,
            output_message=message
        )
