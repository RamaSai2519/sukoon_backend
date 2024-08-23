from models.interfaces import GetEventUsersInput as Input, Output
from db.events import get_event_users_collection
from models.constants import OutputStatus
from models.common import jsonify


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.projection = {"createdAt": 0, "updatedAt": 0, "_id": 0}
        self.offset = int((int(input.page) - 1) * int(input.size))
        self.event_users_collection = get_event_users_collection()

    def prepare_query(self) -> dict:
        if self.input.slug:
            query = {"source": self.input.slug}
        else:
            query = {}
        return query

    def compute(self) -> Output:
        query = self.prepare_query()
        event_users = list(self.event_users_collection.find(
            query, self.projection).skip(self.offset).limit(int(self.input.size)))

        event_users = [jsonify(event_user) for event_user in event_users]

        return Output(
            output_details=event_users,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched events"
        )
