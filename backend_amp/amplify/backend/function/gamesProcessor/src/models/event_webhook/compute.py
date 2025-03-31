from shared.models.interfaces import EventWebhookInput as Input, Output, Event
from shared.db.events import get_events_collection
from shared.models.constants import OutputStatus
from shared.configs import CONFIG as config
from shared.models.common import Common
import requests


class Compute:
    def __init__(self, input: Input) -> None:
        self.event = None
        self.input = input
        self.events_collection = get_events_collection()

    def queue_wa_msgs_for_joined_users(self):
        payload = {
            'action': 'send',
            'event_joined': True,
            'initiatedBy': 'webhook',
            'event_id': self.input.slug,
            'template': 'EVENT_FEEDBACK_SURVEY',
            'params': {'main_title': self.input.main_title}
        }
        url = config.MARK_URL + '/flask/queue_wa_msgs'
        response = requests.post(url, json=payload)
        print(response.json())
        if response.status_code != 200:
            return False
        return True

    def get_event_details(self) -> Event:
        query = {'slug': self.input.slug}
        event = self.events_collection.find_one(query)
        if not event:
            return None
        event = Common.clean_dict(event, Event)
        event = Event(**event)
        self.event = event
        return event

    def remind_users(self) -> bool:
        payload = {
            'action': 'send',
            'event_joined': False,
            'initiatedBy': 'webhook',
            'event_id': self.input.slug,
            'template': 'EVENT_REMINDER_NOT_JOINED',
            'params': {
                'user_name': 'User',
                'link': self.event.meetingLink,
                'main_title': self.input.main_title,
                # 'link': f'https://event.sukoonunlimited.com/d/l?slug={self.input.slug}'}
            }
        }
        url = config.MARK_URL + '/flask/queue_wa_msgs'
        response = requests.post(url, json=payload)
        print(response.json())
        if response.status_code != 200:
            return False
        return True

    def compute(self) -> Output:
        event = self.get_event_details()
        if not event:
            return Output(
                output_status=OutputStatus.FAILURE,
                output_message="Event not found",
            )

        if self.input.event_ended == True:
            response = self.queue_wa_msgs_for_joined_users()
            if not response:
                return Output(
                    output_status=OutputStatus.FAILURE,
                    output_message="Failed to queue wa msgs",
                )
        else:
            response = self.remind_users()
            if not response:
                return Output(
                    output_status=OutputStatus.FAILURE,
                    output_message="Failed to queue wa msgs",
                )

        return Output(
            output_message="Successfully queued wa msgs",
        )
