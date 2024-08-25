from models.interfaces import EventUserInput as Input, User, EventUser, Output
from db.events import get_event_users_collection
from models.constants import OutputStatus
from db.users import get_user_collection
from models.common import jsonify
from dataclasses import asdict
from datetime import datetime
from bson import ObjectId
from typing import Union


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.current_date = datetime.now()
        self.user_collection = get_user_collection()
        self.event_users_collection = get_event_users_collection()

    def find_user(self, phone: str) -> Union[User, None]:
        user = self.user_collection.find_one({"phoneNumber": phone})
        return User(**user) if user else None

    def find_event_user(self, phone: str, source: str) -> Union[EventUser, None]:
        event_user = self.event_users_collection.find_one(
            {"phoneNumber": phone, "source": source}, {"createdAt": 0, "updatedAt": 0})
        return EventUser(**event_user) if event_user else None

    def create_user(self) -> User:
        input = self.input
        user = User(
            isBlocked=False, isPaidUser=False,
            name=input.name or "", refCode=input.source,
            phoneNumber=input.phoneNumber, numberOfCalls=3,
            city=input.city or "", email=input.email or "",
            active=True, isBusy=False, wa_opt_out=False, numberOfGames=0, otp="",
            birthDate=datetime.strptime(
                input.dob, "%Y-%m-%dT%H:%M:%S.%fZ") if input.dob else ""
        )
        user.profileCompleted = bool(
            user.name and user.city and user.birthDate)
        return user

    def create_event_user(self, user: User) -> EventUser:
        input = self.input
        event_user = EventUser(
            eventName=input.eventName or "", advSeenOn=input.advSeenOn or "",
            userId=user._id, name=user.name, city=user.city, email=user.email,
            dob=user.birthDate, phoneNumber=user.phoneNumber, source=input.source or ""
        )
        return event_user

    def insert_event_user(self, event_user: EventUser) -> EventUser:
        event_user_dict = asdict(event_user)
        event_user_dict.pop("_id")
        inserted_id = self.event_users_collection.insert_one(
            event_user_dict).inserted_id
        event_user._id = ObjectId(inserted_id)
        return

    def insert_user(self, user: User) -> User:
        user_dict = asdict(user)
        user_dict.pop("_id")
        inserted_id = self.user_collection.insert_one(user_dict).inserted_id
        user._id = ObjectId(inserted_id)
        return user

    def create_message(self, exists: bool, custom: str = "") -> str:
        if exists:
            return f'{custom}User with phone number {self.input.phoneNumber} already exists'
        return f'{custom}User with phone number {self.input.phoneNumber} created successfully'

    def compute(self) -> Output:
        user = self.find_user(self.input.phoneNumber)
        user_message = self.create_message(True)
        if not user:
            user = self.create_user()
            user = self.insert_user(user)
            user_message = self.create_message(False)

        event_user = self.find_event_user(
            self.input.phoneNumber, self.input.source)
        event_message = self.create_message(True, "Event ")
        if not event_user:
            event_user = self.create_event_user(user)
            event_user = self.insert_event_user(event_user)
            event_message = self.create_message(False, "Event ")

        event_user = self.find_event_user(
            self.input.phoneNumber, self.input.source)
        return Output(
            output_details=jsonify(event_user.__dict__),
            output_status=OutputStatus.SUCCESS,
            output_message=f'{user_message}. {event_message}'
        )
