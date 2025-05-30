import random
import string
import requests
import threading
from bson import ObjectId
from datetime import timedelta
from shared.models.common import Common
from shared.configs import CONFIG as config
from shared.db.events import get_events_collection
from shared.models.interfaces import Event as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.events_collection = get_events_collection()
        self.existing_slugs = self.events_collection.distinct('slug')

    def validate_slug(self, slug: str) -> bool:
        return True if slug in self.existing_slugs else False

    def generate_slug(self) -> str:
        while True:
            slug = ''.join(random.choices(string.ascii_lowercase, k=3))
            if not self.validate_slug(slug):
                return slug

    def prep_data(self, event_data: dict, new_event=True):
        date_fields = ['validUpto',
                       'registrationAllowedTill', 'startEventDate']
        for field in date_fields:
            event_data[field] = Common.string_to_date(event_data, field)

        if new_event:
            event_data["slug"] = self.generate_slug()
            event_data["createdAt"] = self.common.current_time
        event_data["updatedAt"] = self.common.current_time

        if self.input.isDeleted == True:
            event_data["deletedBy"] = ObjectId(self.common.get_identity())

        if "sub_category" in event_data:
            if isinstance(event_data["sub_category"], list):
                event_data["sub_category"] = [
                    ObjectId(item) if isinstance(item, str) else item
                    for item in event_data["sub_category"]
                ]

        event_data = Common.filter_none_values(event_data)
        return event_data

    def schedule_webhooks(self, event_data: dict):
        url = 'https://americano.sukoonunlimited.com/time/schedule'
        start_time = Common.string_to_date(event_data, 'startEventDate')
        slug = event_data.get('slug', 'schedule_webhooks')
        payload2 = {
            'apiUrl': config.URL + '/actions/event_webhook',
            'runAt': start_time + timedelta(minutes=95),
            'body': {
                'slug': slug,
                'event_ended': True,
                'main_title': event_data['mainTitle'],
            }
        }
        payload1 = {
            'apiUrl': config.URL + '/actions/event_webhook',
            'runAt': start_time + timedelta(minutes=10),
            'body': {
                'slug': slug,
                'event_ended': False,
                'main_title': event_data['mainTitle'],
            }
        }
        payload1 = Common.jsonify(payload1)
        payload2 = Common.jsonify(payload2)
        response1 = requests.post(url, json=payload1)
        response_dict1 = response1.json()
        print(f"Webhook scheduled: {response_dict1}")
        response2 = requests.post(url, json=payload2)
        response_dict2 = response2.json()
        print(f"Webhook scheduled: {response_dict2}")

    def compute(self) -> Output:
        event_data = self.input.__dict__

        if self.validate_slug(event_data["slug"]):
            event_data = self.prep_data(event_data, new_event=False)
            self.events_collection.update_one(
                {"slug": event_data["slug"]},
                {"$set": event_data}
            )
            message = "Successfully updated event"
        else:
            event_data = self.prep_data(event_data)
            self.events_collection.insert_one(event_data)
            self.schedule_webhooks(event_data)
            message = "Successfully created event"

        return Output(
            output_details=Common.jsonify(event_data),
            output_message=message
        )
