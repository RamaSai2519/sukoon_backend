from shared.models.interfaces import CreateContributeInterestInput as Input, Output, ContributeInterest
from shared.db.events import get_contirbute_event_users_collection, get_contribute_events_collection
from shared.models.constants import OutputStatus
from shared.db.users import get_user_collection
from shared.configs import CONFIG as config
from shared.models.common import Common
from bson import ObjectId
import requests


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()
        self.collection = get_contirbute_event_users_collection()
        self.events_collection = get_contribute_events_collection()

    def validate_interest(self) -> bool:
        query = {
            "slug": self.input.slug,
            "user_id": ObjectId(self.input.user_id)
        }
        interest = self.collection.find_one(query)
        return True if interest else False

    def send_details(self, user_name: str, phoneNumber: str, event: dict) -> dict:
        url = config.URL + "/actions/send_whatsapp"
        payload = {
            'phone_number': phoneNumber,
            'template_name': 'CONTRIBUTE_UTILITY_USER_RESPONSE',
            'parameters': {
                'user_name': user_name.split(' ')[0],
                'event_name': event.get('name', 'Not Available'),
                'role': event.get('description', 'Contact the below number').replace('#', ''),
                'address': event.get('company', 'Contact the below number'),
                'phone_number': event.get('phoneNumber', 'Not Available'),
            }
        }
        response = requests.post(url, json=payload)
        output = response.json()
        failure_message = 'Failed to send details'
        if 'output_status' not in output:
            return failure_message
        if output['output_status'] == OutputStatus.SUCCESS:
            return 'Details sent successfully'
        return failure_message

    def get_event(self) -> dict:
        query = {"slug": self.input.slug}
        event = self.events_collection.find_one(query)
        return event

    def get_user(self) -> dict:
        query = {"_id": ObjectId(self.input.user_id)}
        user = self.users_collection.find_one(query)
        return user

    def validate_docs(self, user: dict, event: dict) -> Output:
        if not event:
            return Output(
                output_status=OutputStatus.FAILURE,
                output_message="Invalid event slug"
            )
        if not user:
            return Output(
                output_status=OutputStatus.FAILURE,
                output_message="Invalid user ID"
            )

    def compute(self) -> Output:
        event = self.get_event()
        user = self.get_user()
        if self.validate_docs(user, event):
            return self.validate_docs(user, event)

        if self.validate_interest():
            return Output(
                output_status=OutputStatus.FAILURE,
                output_message="Interest already exists"
            )

        club_interest = ContributeInterest(
            slug=self.input.slug,
            user_id=ObjectId(self.input.user_id)
        )
        data = club_interest.__dict__
        data = {k: v for k, v in data.items() if v is not None}
        self.collection.insert_one(data)

        user_number = user['phoneNumber']
        user_name = user.get('name', 'User')
        message = self.send_details(user_name, user_number, event)

        return Output(
            output_message="Interest created successfully. " + message,
            output_details=Common.jsonify(data)
        )
