from models.interfaces import EventUserInput as Input, Output
from db.events import get_event_users_collection
from models.constants import OutputStatus
from db.users import get_user_collection
from datetime import datetime
from bson import ObjectId
from pprint import pprint


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.current_date = datetime.now()
        self.user_collection = get_user_collection()
        self.event_users_collection = get_event_users_collection()

    def find_user(self, phone: str) -> dict | None:
        user = self.user_collection.find_one({"phoneNumber": phone})
        return user if user else None

    def find_event_user(self, phone: str) -> dict | None:
        event_user = self.event_users_collection.find_one(
            {"phoneNumber": phone}, {"createdAt": 0, "updatedAt": 0})
        return event_user if event_user else None

    def create_user(self) -> dict:
        current_date = self.current_date
        user = {
            "otp": "",
            "active": True,
            "isBusy": False,
            "numberOfCalls": 3,
            "numberOfGames": 0,
            "isBlocked": False,
            "isPaidUser": False,
            "wa_opt_out": False,
            "expiresOtp": current_date,
            "createdDate": current_date,
            "name": self.input.name if self.input.name else "",
            "city": self.input.city if self.input.city else "",
            "email": self.input.email if self.input.email else "",
            "phoneNumber": self.input.phone if self.input.phone else "",
            "refCode": self.input.eventName if self.input.eventName else "",
            "birthDate": datetime.strptime(self.input.dob, "%Y-%m-%dT%H:%M:%S.%fZ") if self.input.dob else "",
        }
        if self.input.name and self.input.city and self.input.dob:
            user["profileCompleted"] = True
        else:
            user["profileCompleted"] = False

        new_user_id = self.user_collection.insert_one(user).inserted_id
        user["_id"] = ObjectId(new_user_id)
        return user

    def create_event_user(self, user: dict) -> dict:
        current_date = self.current_date
        event_user = {
            "userId": user["_id"],
            "createdAt": current_date,
            "updatedAt": current_date,
            "phoneNumber": user["phoneNumber"],
            "name": user["name"] if user["name"] else "",
            "city": user["city"] if user["city"] else "",
            "email": user["email"] if user["email"] else "",
            "dob": user["birthDate"] if user["birthDate"] else "",
            "source": self.input.source if self.input.source else "",
            "eventName": self.input.eventName if self.input.eventName else "",
            "advSeenOn": self.input.advSeenOn if self.input.advSeenOn else "",
        }
        new_event_user_id = self.event_users_collection.insert_one(
            event_user).inserted_id
        event_user["_id"] = ObjectId(new_event_user_id)
        return event_user

    def __format__(self, event_user: dict) -> dict:
        event_user["_id"] = str(event_user["_id"])

        if "userId" in event_user:
            event_user["userId"] = str(event_user["userId"])

        if "dob" in event_user:
            event_user["dob"] = datetime.strftime(
                event_user["dob"], "%Y-%m-%dT%H:%M:%S")

        if "createdAt" in event_user:
            event_user.pop("createdAt")

        if "updatedAt" in event_user:
            event_user.pop("updatedAt")

        return event_user

    def compute(self) -> Output:
        user = self.find_user(self.input.phone)
        if not user:
            user = self.create_user()

        event_user = self.find_event_user(self.input.phone)
        if not event_user:
            event_user = self.create_event_user(user)
        event_user = self.__format__(event_user)
        pprint(event_user)

        return Output(
            output_details=event_user,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully registered user to event"
        )
