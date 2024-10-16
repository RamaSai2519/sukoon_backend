import pytz
from datetime import datetime
from slack_sdk import WebClient
from configs import CONFIG as config
from slack_sdk.errors import SlackApiError


class WASlackNotifier:
    def __init__(self, from_number: str, name: str, body: str) -> None:
        self.from_number = from_number
        self.name = name
        self.body = body
        self.channel = "C07DYT3RS4T"
        self.timezone = pytz.timezone("Asia/Kolkata")
        self.client = WebClient(token=config.SARATHI_SLACK_BOT_TOKEN)

    def join_channel(self) -> None:
        try:
            self.client.conversations_join(channel=self.channel)
        except SlackApiError as e:
            print(f"Error joining channel: {e}")

    def _create_message_blocks(self) -> list:
        """Compose the message blocks with user information."""
        blocks = [
            {
                "type": 'section',
                "text": {
                    "type": 'mrkdwn',
                    "text": f'<!channel> User with phone number *{self.from_number}* named *{self.name}* has sent *{self.body}*',
                },
            },
            {
                "type": 'section',
                "fields": [
                    {
                        "type": 'mrkdwn',
                        "text": f'*Time:*\n{datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S")}',
                    },
                    {
                        "type": 'mrkdwn',
                        "text": f'*Phone Number:*\n{self.from_number}',
                    },
                    {
                        "type": 'mrkdwn',
                        "text": f'*Message Body:*\n{self.body}',
                    }
                ]
            }
        ]
        return blocks

    def send_notification(self) -> str:
        """Send the Slack notification with the constructed message."""
        blocks = self._create_message_blocks()
        try:
            self.join_channel()
            response = self.client.chat_postMessage(
                channel=self.channel,
                blocks=blocks,
                text=f"Notification from {self.name}"
            )
            if response["ok"]:
                return f"Notification sent to Slack"
            else:
                return f"Failed to send notification: {response}"
        except SlackApiError as e:
            return f"Error sending notification: {e.response['error']}"
