from shared.db.events import get_events_collection, get_event_users_collection
from shared.db.users import get_user_collection, get_user_fcm_token_collection
from shared.db.misc import get_counters_collection
from shared.models.constants import TimeFormats
from shared.models.interfaces import Output
from shared.configs import CONFIG as config
from datetime import timedelta, datetime
from shared.models.common import Common
from bson import ObjectId
import requests
import pytz


class Compute:
    def __init__(self) -> None:
        self.common = Common()
        self.collection = get_events_collection()
        self.users_collection = get_user_collection()
        self.now_time = Common.get_current_utc_time()
        self.counters_collection = get_counters_collection()
        self.tokens_collection = get_user_fcm_token_collection()
        self.event_users_collection = get_event_users_collection()

    def get_difference(self, validUpto: datetime) -> int:
        validUpto = validUpto.replace(tzinfo=pytz.utc)
        difference: timedelta = validUpto - self.now_time
        return int(difference.total_seconds() // 60)

    def send_whatsapp(self, reminder: dict) -> str:
        url = config.URL + "/actions/send_whatsapp"
        payload = {
            'phone_number': reminder['user_phone'],
            'template_name': 'EVENT_REMINDER_MINUTES',
            'parameters': {
                'user_name': reminder['user_name'] or 'User',
                'event_name': reminder['event_name'],
                'meeting_link': reminder['meeting_link'],
                'minutes': str(self.get_difference(reminder['validUpto']))
            }, 'skip_check': True
        }
        response = requests.post(url, json=payload)
        return response.text

    def send_notification(self, reminder: dict, token: str) -> str:
        url = config.URL + "/actions/push"
        payload = {
            'token': token,
            'type_': 'user',
            'sound': 'bell',
            'app_type': 'user',
            'priority': 'high',
            'image_url': reminder['image_url'],
            'title': f'Join Here: {reminder["meeting_link"]}',
            'body': f'{reminder["event_name"]} is starting in {self.get_difference(reminder["validUpto"])} minutes',
        }
        response = requests.post(url, json=payload)
        return response.text

    def get_fcm_token(self, phoneNumber: str) -> str:
        user = self.users_collection.find_one({'phoneNumber': phoneNumber})
        user_id = user['_id']
        query = {'userId': str(user_id)}
        tokens = self.tokens_collection.find(
            query).sort('createdAt', -1).limit(1)
        tokens = list(tokens) if tokens else []
        if tokens != []:
            return tokens[0]['fcmToken']
        return None

    def job(self, reminder: dict) -> bool:
        token = self.get_fcm_token(reminder['user_phone'])
        if token:
            self.send_notification(reminder, token)
        self.send_whatsapp(reminder)
        return True

    def get_reminders(self) -> list:
        query = {'type': 'event_reminders', 'done': False}
        reminders = self.counters_collection.find(query)
        return list(reminders) if reminders else []

    def compute(self) -> Output:
        reminders = self.get_reminders()
        if reminders == []:
            return Output(output_message='No reminders found')
        for reminder in reminders:
            self.job(reminder)
            self.counters_collection.update_one(
                {'_id': ObjectId(reminder['_id'])}, {'$set': {'done': True, 'sent_at': self.now_time}})
        return Output(output_message='Reminders sent')
