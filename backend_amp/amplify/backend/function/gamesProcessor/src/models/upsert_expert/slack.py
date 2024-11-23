import pytz
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from shared.configs import CONFIG as config


class SlackManager:
    def __init__(self):
        self.client = WebClient(token=config.SARATHI_SLACK_BOT_TOKEN)
        self.channel = "C07FK8DJLJC"
        self.timezone = pytz.timezone("Asia/Kolkata")
        self.dashboard_url = "https://admin.sukoonunlimited.com/admin/experts/"

    def join_channel(self):
        try:
            self.client.conversations_join(channel=self.channel)
        except SlackApiError as e:
            print(f"Error joining channel: {e}")

    def compose_message(self, status: bool, expert_name: str, expert_number: str):
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
                        "text": 'Check Sarathi Timings',
                    },
                    "value": 'expert_timings',
                    "url": f"{self.dashboard_url}{expert_number}#timings",
                    "action_id": 'button_expert_timings',
                },
            ],
        }

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"@channel *{expert_name}* is now *{'online' if status else 'offline'}*. {'🎉' if status else '🚫'}"
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
                        "text": f'*Status:*\n{"Online" if status else "Offline"}'
                    }
                ]
            },
            actions_block
        ]
        return blocks

    def send_message(self, status: bool, expert_name: str, expert_number: str) -> str:
        message = self.compose_message(status, expert_name, expert_number)
        try:
            self.join_channel()
            response = self.client.chat_postMessage(
                channel=self.channel,
                blocks=message,
                text=f"{expert_name} is now" +
                'online' if status else 'offline'
            )
            if response["ok"]:
                message = "Status Message sent to channel"
            else:
                message = f"Error sending status message: {response}"
            return message
        except SlackApiError as e:
            print(f"Error: {e}")
            return f"Error sending status message: {e.response['error']}"
