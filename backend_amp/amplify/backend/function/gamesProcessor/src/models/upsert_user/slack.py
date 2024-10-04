import pytz
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from configs import CONFIG as config


class SlackManager:
    def __init__(self) -> None:
        self.client = WebClient(token=config.USER_SLACK_BOT_TOKEN)
        self.channel = "C07R58933DW"
        self.timezone = pytz.timezone("Asia/Kolkata")
        self.dashboard_url = "https://admin.sukoonunlimited.com/admin/users/"

    def join_channel(self) -> None:
        try:
            self.client.conversations_join(channel=self.channel)
        except SlackApiError as e:
            print(f"Error joining channel: {e}")

    # -> list[dict[str, Any]]:
    def compose_message(self, user_name: str, type: str, user_id: str) -> list:
        details_block = {
            "type": 'section',
            "text": {
                "type": 'mrkdwn',
                "text": '*Details:*',
            },
        }
        actions_block = {
            "type": 'actions',
            "elements": [
                {
                    "type": 'button',
                    "text": {
                        "type": 'plain_text',
                        "text": 'Check User Details',
                    },
                    "value": 'user_details',
                    "url": f"{self.dashboard_url}{user_id}",
                    "action_id": 'button_user_details',
                },
            ],
        }

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"@channel *{user_name}* has just signed up as a *{type}* {'🎉' if type == 'User' else '👍'}"
                }
            },
            details_block,
            {
                "type": 'section',
                "fields": [
                    {
                        "type": 'mrkdwn',
                        "text": f'*Time:*\n{datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S")}'
                    },
                    {
                        "type": 'mrkdwn',
                        "text": f'*Type:*\n{type}'
                    }
                ]
            },
            actions_block
        ]
        return blocks

    def send_message(self, user_name: str, type: str, user_id: str) -> str:
        message = self.compose_message(user_name, type, user_id)
        try:
            self.join_channel()
            response = self.client.chat_postMessage(
                channel=self.channel,
                blocks=message,
                text=f"{user_name} has just signed up"
            )
            if response["ok"]:
                message = " and signup Message sent to channel"
            else:
                message = f" but Error sending signup message: {response}"
            return message
        except SlackApiError as e:
            print(f"Error: {e}")
            return f" but Error sending signup message: {e.response['error']}"
