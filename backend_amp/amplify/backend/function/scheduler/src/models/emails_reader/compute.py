from shared.db.misc import get_emails_collection
from shared.configs import CONFIG as config
from shared.models.interfaces import Output
from shared.models.common import Common
from .email_client import EmailClient
from .email_parser import EmailParser
import requests
import re


class Compute:
    def __init__(self) -> None:
        self.input_str = None
        self.collection = get_emails_collection()
        self.current_time = Common.get_current_utc_time()

    def get_emails(self) -> list:
        query = {'sender_mails': {'$exists': True}}
        doc = self.collection.find_one(query)
        return list(doc['sender_mails'])

    def _extract_detail(self, pattern: str) -> str:
        match = re.search(pattern, self.input_str)
        return match.group(1).strip() if match else None

    def extract_details(self) -> dict:
        details = {}
        details['name'] = self._extract_detail(r'Name:\s*(.*?)(?:\r\n|<)')
        details['phoneNumber'] = self._extract_detail(
            r'Phone:\s*(\d+)(?:\r\n|<)')
        details['city'] = self._extract_detail(r'City:\s*(.*?)(?:\r\n|<)')
        details['refSource'] = self._extract_detail(
            r'Source:\s*(.*?)(?:\r\n|<)')
        return details

    def compute(self) -> Output:
        emails = self.get_emails()
        today = self.current_time.strftime("%d-%b-%Y")
        client = EmailClient()

        for email in emails:
            search_criteria = f'FROM "{email}" SINCE "{today}"'
            emails = client.search_emails(search_criteria)

            for email_id in emails:
                msg = client.fetch_email(email_id)
                email_data = EmailParser.parse_email(msg)

                query = {
                    'subject': email_data['subject'], 'body': email_data['body']}
                self.collection.find_one_and_update(
                    query, {'$set': email_data}, upsert=True)

                self.input_str = email_data['body']
                details = self.extract_details()
                if len(details['phoneNumber']) == 10:
                    url = config.URL + '/actions/user'
                    payload = details
                    response = requests.post(url, json=payload)
                    print(response.text)

        client.logout()
        return Output(output_message='Successfully processed emails')
