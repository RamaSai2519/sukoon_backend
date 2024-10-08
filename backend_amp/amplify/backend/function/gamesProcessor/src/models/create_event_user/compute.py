from models.interfaces import EventUserInput as Input, User, EventUser, Output, UserMeta
from models.constants import OutputStatus, application_json_header
from db.users import get_user_collection, get_meta_collection
from db.events import get_event_users_collection
from pymongo.collection import Collection
from configs import CONFIG as config
from models.common import Common
from dataclasses import asdict
from datetime import datetime
from bson import ObjectId
from typing import Union
import requests
import json


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.url = config.URL + "/actions/user"
        self.current_date = datetime.now()
        self.meta_collection = get_meta_collection()
        self.user_collection = get_user_collection()
        self.event_users_collection = get_event_users_collection()

    def find_user(self, phone: str) -> Union[User, None]:
        user = self.user_collection.find_one({"phoneNumber": phone})
        user = Common.clean_dict(user, User)
        return User(**user) if user else None

    def find_event_user(self, phone: str, source: str) -> Union[EventUser, None]:
        event_user = self.event_users_collection.find_one(
            {"phoneNumber": phone, "source": source}, {"createdAt": 0, "updatedAt": 0})
        event_user = Common.clean_dict(event_user, EventUser)
        return EventUser(**event_user) if event_user else None

    def create_user(self) -> User:
        input = self.input
        user = User(
            name=input.name or "", refCode=input.source or "",
            phoneNumber=input.phoneNumber, city=input.city or "", email=input.email or "",
            birthDate=datetime.strptime(
                input.dob, "%Y-%m-%dT%H:%M:%S.%fZ") if input.dob else ""
        )
        return user

    def create_event_user(self, user: User) -> EventUser:
        input = self.input
        event_user = EventUser(
            eventName=input.eventName or "", advSeenOn=input.advSeenOn or "",
            userId=user._id, name=user.name, city=user.city, email=user.email,
            dob=user.birthDate, phoneNumber=user.phoneNumber, source=input.source or ""
        )
        return event_user

    def insert_event_user(self, user: Union[EventUser, User], collection: Collection) -> Union[EventUser, User]:
        event_user_dict = asdict(user)
        event_user_dict.pop("_id")
        inserted_id = collection.insert_one(event_user_dict).inserted_id
        user._id = ObjectId(inserted_id)
        return user

    def insert_user(self, user: User) -> User:
        user_dict = asdict(user)
        payload = json.dumps(Common.jsonify(user_dict))
        response = requests.request(
            "POST", self.url, headers=application_json_header, data=payload)
        user._id = response.json().get("output_details").get("_id")
        return user

    def create_message(self, exists: bool, custom: str = "") -> str:
        if exists:
            return f'{custom}User with phone number {self.input.phoneNumber} already exists'
        return f'{custom}User with phone number {self.input.phoneNumber} created successfully'

    def insert_meta(self, user_id: str) -> None:
        user_meta = UserMeta(user=ObjectId(user_id), source='events')
        insertion = self.meta_collection.insert_one(asdict(user_meta))
        print(insertion)

    def compute(self) -> Output:
        user = self.find_user(self.input.phoneNumber)
        user_message = self.create_message(True)
        if not user:
            user = self.create_user()
            user = self.insert_user(user)
            self.insert_meta(user._id)
            user_message = self.create_message(False)

        event_user = self.find_event_user(
            self.input.phoneNumber, self.input.source)
        event_message = self.create_message(True, "Event ")
        if not event_user:
            event_user = self.create_event_user(user)
            event_user = self.insert_event_user(
                event_user, self.event_users_collection)
            event_message = self.create_message(False, "Event ")

        event_user = self.find_event_user(
            self.input.phoneNumber, self.input.source)
        return Output(
            output_details=Common.jsonify(event_user.__dict__),
            output_status=OutputStatus.SUCCESS,
            output_message=f'{user_message}. {event_message}'
        )
