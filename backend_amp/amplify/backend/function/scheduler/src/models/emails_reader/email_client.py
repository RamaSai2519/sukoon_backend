import email
import imaplib
from typing import List
from email.message import Message
from shared.configs import CONFIG as config


class EmailClient:
    def __init__(self) -> None:
        self.username = config.EMAIL_CONFIG['username']
        self.password = config.EMAIL_CONFIG['password']
        self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
        self.mail.login(self.username, self.password)

    def search_emails(self, search_criteria: str = 'ALL') -> List[bytes]:
        self.mail.select("inbox")
        status, messages = self.mail.search(None, search_criteria)
        return messages[0].split()

    def fetch_email(self, email_id: bytes) -> Message:
        status, msg_data = self.mail.fetch(email_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                return email.message_from_bytes(response_part[1])

    def logout(self) -> None:
        self.mail.logout()
