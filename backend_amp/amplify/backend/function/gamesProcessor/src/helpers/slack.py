import requests


class SlackNotifier:
    def __init__(self):
        self.webhook_url = "https://hooks.slack.com/services/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"

    def _get_status_message(self, status):
        status_mapping = {
            'success': ('Call initiated successfully', ':tada:'),
            'sarathi_busy': ('Sarathi is busy', ':red_circle:'),
            'user_busy': ('User is busy', ':red_circle:'),
            'balance_low': ('Not enough balance', ':warning:'),
            'offline': ('Sarathi is offline', ':no_entry:')
        }
        return status_mapping.get(status, ('Unknown status', ':grey_question:'))

    def _create_message_blocks(self, type_, user_name, sarathi_name, status, call_link='', dashboard_link='https://admin.sukoonunlimited.com/admin/home/calls%20list'):
        status_message, status_emoji = self._get_status_message(status)

        blocks = [
            {
                "type": 'section',
                "text": {
                    "type": 'mrkdwn',
                    "text": f'<!channel> *{status_message}* between *{sarathi_name}* and *User: {user_name}* {status_emoji}',
                },
            },
            {
                "type": 'section',
                "text": {
                    "type": 'mrkdwn',
                    "text": '*Details:*',
                },
            },
            {
                "type": 'section',
                "fields": [
                    {
                        "type": 'mrkdwn',
                        "text": f'*Sarathi:*\n{sarathi_name}',
                    },
                    {
                        "type": 'mrkdwn',
                        "text": f'*User:*\n{user_name}',
                    },
                ],
            },
            {
                "type": 'section',
                "fields": [
                    {
                        "type": 'mrkdwn',
                        "text": f'*Status:*\n{status_message}',
                    },
                    {
                        "type": 'mrkdwn',
                        "text": f'*Call Type:*\n{type_}',
                    }
                ],
            },
        ]

        if status == 'success' and call_link:
            blocks.append({
                "type": 'actions',
                "elements": [
                    {
                        "type": 'button',
                        "text": {
                            "type": 'plain_text',
                            "text": 'Join Call',
                        },
                        "value": 'join_call',
                        "url": call_link,
                        "action_id": 'button_join_call',
                    }
                ]
            })

        if dashboard_link:
            blocks[-1]["elements"].append({
                "type": 'button',
                "text": {
                    "type": 'plain_text',
                    "text": 'Go to Admin Dashboard',
                },
                "value": 'admin_dashboard',
                "url": dashboard_link,
                "action_id": 'button_admin_dashboard',
            })

        return blocks

    def send_notification(self, type_, user_name, sarathi_name, status, call_link='', dashboard_link=''):
        blocks = self._create_message_blocks(
            type_, user_name, sarathi_name, status, call_link, dashboard_link)

        try:
            response = requests.post(
                self.webhook_url, json={"blocks": blocks})
            if response.status_code == 200:
                print(f"Notification sent to Slack: {response.text}")
            else:
                print(f"Failed to send notification: {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending notification: {e}")
