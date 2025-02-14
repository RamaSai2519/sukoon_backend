from shared.db.events import get_events_collection, get_event_users_collection
from shared.db.misc import get_counters_collection
from shared.db.users import get_user_collection
from shared.models.interfaces import Output
from datetime import timedelta, datetime
from shared.models.common import Common
import pytz


class Compute:
    def __init__(self) -> None:
        self.common = Common()
        self.collection = get_events_collection()
        self.users_collection = get_user_collection()
        self.now_time = Common.get_current_utc_time()
        self.counters_collection = get_counters_collection()
        self.event_users_collection = get_event_users_collection()

    def get_events(self) -> list:
        query = {'name': 'event_reminder_buffer'}
        doc = self.counters_collection.find_one(query)
        if not doc:
            doc = {
                'name': 'event_reminder_buffer',
                'minutes': 30,
            }
            self.counters_collection.insert_one(doc)
        minutes = doc['minutes'] + 1
        query = {
            'validUpto': {
                "$gt": self.now_time - timedelta(minutes=1),
                "$lt": self.now_time + timedelta(minutes=minutes)
            },
            # 'isDeleted': False
        }
        events = self.collection.find(query)
        return list(events) if events else []

    def compute(self) -> Output:
        events = self.get_events()
        if events == []:
            return Output(output_message='No events found')
        for event in events:
            query = {'source': event['slug']}
            users = self.event_users_collection.find(query)
            docs = []
            for user in users:
                doc = {
                    'user_name': user.get('name', user['phoneNumber']),
                    'user_phone': user['phoneNumber'],
                    'meeting_link': event['meetingLink'],
                    'event_name': event['mainTitle'],
                    'validUpto': event['validUpto'],
                    'image_url': event['imageUrl'],
                    'type': 'event_reminders',
                    'name': event['slug'],
                    'done': False
                }
                query = {'user_phone': user['phoneNumber'],
                         'name': event['slug'], 'type': 'event_reminders'}
                prev_doc = self.counters_collection.find_one(query)
                if not prev_doc:
                    self.counters_collection.insert_one(doc)
            return Output(output_message='Inserted reminders')
        return Output(output_message='No users found')
