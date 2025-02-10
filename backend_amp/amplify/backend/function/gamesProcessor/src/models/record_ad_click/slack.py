from bson import ObjectId
from slack_sdk import WebClient
from shared.models.common import Common
from slack_sdk.errors import SlackApiError
from shared.configs import CONFIG as config
from shared.db.referral import get_prcs_collection


class SlackManager:
    def __init__(self) -> None:
        self.common = Common()
        self.channel = 'C08D72NCA1W'
        self.collection = get_prcs_collection()
        self.client = WebClient(token=config.SARATHI_SLACK_BOT_TOKEN)

    def join_channel(self) -> None:
        try:
            self.client.conversations_join(channel=self.channel)
        except SlackApiError as e:
            print(f"Error joining channel: {e}")

    def compose_message(self, partner: str) -> list:
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"@channel A User signed up via *{partner}*"
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

    def get_partner_name(self, prc: str) -> str:
        query = {'token': prc}
        doc = self.collection.find_one(query)
        if doc:
            return doc['name']
        return 'Unknown'

    def send_message(self, prc: str) -> str:
        partner = self.get_partner_name(prc)
        message = self.compose_message(partner)
        try:
            self.join_channel()
            response = self.client.chat_postMessage(
                channel=self.channel,
                blocks=message,
                text=f"Call has failed"
            )
            if response["ok"]:
                message = " and Message sent to channel"
            else:
                message = f" but Error sending message: {response}"
            return message
        except SlackApiError as e:
            print(f"Error: {e}")
            return f" but Error sending message: {e.response['error']}"
