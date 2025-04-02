import random
import string
import requests
import threading
from bson import ObjectId
from pprint import pprint
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
        payloads = [
            {
                'apiUrl': config.URL + '/actions/event_webhook',
                'runAt': start_time + timedelta(minutes=10),
                'body': {
                    'event_ended': False,
                    'slug': event_data['slug'] or 'schedule_webhooks',
                    'main_title': event_data['mainTitle'],
                }
            },
            {
                'apiUrl': config.URL + '/actions/event_webhook',
                'runAt': start_time + timedelta(minutes=95),
                'body': {
                    'event_ended': True,
                    'slug': event_data['slug'] or 'schedule_webhooks',
                    'main_title': event_data['mainTitle'],
                }
            }
        ]
        for payload in payloads:
            payload = Common.jsonify(payload)
            pprint(payload, 'schedule_webhooks')
            response = requests.post(url, json=payload)
            response_dict = response.json()
            print(f"Webhook scheduled: {response_dict}")

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
            threading.Thread(
                target=self.schedule_webhooks, args=(event_data,)
            ).start()
            message = "Successfully created event"

        return Output(
            output_details=Common.jsonify(event_data),
            output_message=message
        )
