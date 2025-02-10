from bson import ObjectId
from slack_sdk import WebClient
from shared.models.common import Common
from slack_sdk.errors import SlackApiError
from shared.configs import CONFIG as config


class SlackManager:
    def __init__(self) -> None:
        self.common = Common()
        self.channel = 'C08CZF9DJP3'
        self.client = WebClient(token=config.SARATHI_SLACK_BOT_TOKEN)

    def join_channel(self) -> None:
        try:
            self.client.conversations_join(channel=self.channel)
        except SlackApiError as e:
            print(f"Error joining channel: {e}")

    def compose_message(self, user_name: str) -> list:
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"@channel Receiving a call from *{user_name}*"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f'*Time:*\n{Common.get_current_ist_time().strftime("%Y-%m-%d %H:%M:%S")}'
                    }
                ]
            }
        ]
        return blocks

    def send_message(self, user_name: str) -> str:
        message = self.compose_message(user_name)
        try:
            self.join_channel()
            response = self.client.chat_postMessage(
                channel=self.channel,
                blocks=message,
                text=f"Receiving a call from {user_name}"
            )
            if response["ok"]:
                message = " and Message sent to channel"
            else:
                message = f" but Error sending message: {response}"
            return message
        except SlackApiError as e:
            print(f"Error: {e}")
            return f" but Error sending message: {e.response['error']}"
