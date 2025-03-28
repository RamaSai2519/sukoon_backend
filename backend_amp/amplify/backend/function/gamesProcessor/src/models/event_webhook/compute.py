from shared.models.interfaces import EventWebhookInput as Input, Output
from shared.models.constants import OutputStatus
from shared.configs import CONFIG as config
import requests


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input

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

    def remind_users(self) -> bool:
        payload = {
            'action': 'send',
            'event_joined': True,
            'initiatedBy': 'webhook',
            'event_id': self.input.slug,
            'template': 'EVENT_REMINDER_NOT_JOINED',
            'params': {
                'user_name': 'User',
                'main_title': self.input.main_title,
                'link': f'https://event.sukoonunlimited.com/d/l?slug={self.input.slug}'}
        }
        url = config.MARK_URL + '/flask/queue_wa_msgs'
        response = requests.post(url, json=payload)
        print(response.json())
        if response.status_code != 200:
            return False
        return True

    def compute(self) -> Output:
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
