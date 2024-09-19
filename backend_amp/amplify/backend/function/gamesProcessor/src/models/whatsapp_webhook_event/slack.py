import requests
from models.interfaces import WASlackNotifierInput as Input


class WASlackNotifier:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.webhook_url = "https://hooks.slack.com/services/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"

    def _create_message_blocks(self) -> list:
        blocks = [
            {
                "type": 'section',
                "text": {
                    "type": 'mrkdwn',
                    "text": f'<!channel> User with phone number *{self.input.from_number}* of name *{self.input.name}* has sent *{self.input.body}*',
                },
            },
        ]

        return blocks

    def send_notification(self):
        blocks = self._create_message_blocks()
        try:
            response = requests.post(
                self.webhook_url, json={"blocks": blocks})
            if response.status_code == 200:
                print(f"Notification sent to Slack: {response.text}")
            else:
                print(f"Failed to send notification: {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending notification: {e}")
