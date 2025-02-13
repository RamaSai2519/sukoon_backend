from shared.models.constants import OutputStatus, application_json_header, TimeFormats, customer_care_number
from shared.models.interfaces import EventUserInput as Input, User, EventUser, Output, UserMeta, Event
from shared.db.events import get_event_users_collection, get_events_collection
from shared.db.users import get_user_collection, get_meta_collection
from shared.configs import CONFIG as config
from pymongo.collection import Collection
from shared.models.common import Common
from datetime import timedelta
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
        self.wa_url = config.URL + "/actions/send_whatsapp"
        self.current_date = datetime.now()
        self.meta_collection = get_meta_collection()
        self.user_collection = get_user_collection()
        self.events_collection = get_events_collection()
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
                input.dob, TimeFormats.ANTD_TIME_FORMAT) if input.dob else ""
        )
        return user

    def create_event_user(self, user: User) -> EventUser:
        input = self.input
        event_user = EventUser(
            eventName=input.eventName or "", advSeenOn=input.advSeenOn or "",
            userId=user._id, name=user.name, city=user.city, email=user.email,
            dob=user.birthDate, phoneNumber=user.phoneNumber, source=input.source or "", isUserPaid=input.isUserPaid or False
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
        self.meta_collection.insert_one(asdict(user_meta))

    def find_event(self) -> Union[Event, None]:
        event = self.events_collection.find_one(
            {"slug": self.input.source})
        event = Common.clean_dict(event, Event)
        return Event(**event) if event else None

    def pop_immutable_fields(self, data: dict) -> dict:
        fields = ["_id", "phoneNumber", "createdAt"]
        for field in fields:
            data.pop(field, None)
        return data

    def prep_data(self, new_data: dict, old_data: dict) -> dict:
        new_data = {k: v for k, v in new_data.items() if v is not None}
        old_data = self.pop_immutable_fields(old_data)
        old_data.update(new_data)
        date_fields = ["dob", "createdAt", "updatedAt"]
        for field in date_fields:
            if isinstance(old_data.get(field), str):
                old_data[field] = Common.string_to_date(old_data, field)
        return old_data

    def send_confirmation(self, user: User, event: Event) -> str:
        url = config.URL + "/actions/send_whatsapp"
        event_date = event.startEventDate
        event_date = event_date + timedelta(hours=5, minutes=30)
        payload = {
            'phone_number': user.phoneNumber,
            'template_name': 'EVENT_REGISTRATION_CONFIRMATION',
            'parameters': {
                'user_name': user.name,
                'topic_name': event.mainTitle,
                'date_and_time': event_date.strftime(TimeFormats.USER_TIME_FORMAT),
                'custom_text': event.subTitle,
                'speakers_name': event.guestSpeaker,
                'event_name': event.mainTitle,
                'image_link': event.imageUrl,
                'webinar_link': event.meetingLink,
                'phone_number': '+91' + customer_care_number,
                'whatsapp_community_link': "https://sukoonunlimited.com/wa-join-community"
            }
        }
        response = requests.post(url, json=payload)
        response_dict = response.json()
        if "output_status" in response_dict and response_dict.get("output_status") == "SUCCESS":
            return "Event details sent"
        return "[event_message] Event details not sent"

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
        nudge_message = ""
        confirmation_message = ""
        if not event_user:
            event_user = self.create_event_user(user)
            event_user = self.insert_event_user(
                event_user, self.event_users_collection)
            event_message = self.create_message(False, "Event ")
            event = self.find_event()

            if event.isPremiumUserOnly == False:
                confirmation_message = self.send_confirmation(user, event)
        else:
            event_user = self.prep_data(asdict(self.input), asdict(event_user))
            self.event_users_collection.update_one(
                {"phoneNumber": self.input.phoneNumber,
                    "source": self.input.source},
                {"$set": event_user}
            )
            event_message = "Event User updated successfully"

        event_user = self.find_event_user(
            self.input.phoneNumber, self.input.source)
        messages = [user_message, event_message,
                    nudge_message, confirmation_message]
        f_message = ". ".join([msg for msg in messages if msg])
        print(f_message)

        return Output(
            output_details=Common.jsonify(event_user.__dict__),
            output_status=OutputStatus.SUCCESS,
            output_message=f_message
        )
