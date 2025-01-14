from shared.models.interfaces import EventUserInput as Input
from shared.db.events import get_events_collection
from shared.db.users import get_user_collection
from shared.models.common import Common


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()
        self.events_collection = get_events_collection()

    def get_user_id(self) -> str:
        query = {'phoneNumber': self.input.phoneNumber}
        user = self.users_collection.find_one(query)
        return str(user['_id'])

    def validate_input(self) -> tuple:
        query = {'slug': self.input.source}
        event: dict = self.events_collection.find_one(query)
        if not event:
            return False, 'Invalid source'

        user_id = self.get_user_id()
        req_balance = 'paid_events' if event.get(
            'isPremiumUserOnly', False) == True else 'free_events'
        if not Common.authorize_action(user_id, req_balance, 'done'):
            return False, 'Invalid Token'

        return True, ''
