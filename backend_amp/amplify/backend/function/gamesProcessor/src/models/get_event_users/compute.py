from models.interfaces import GetEventUsersInput as Input, Output
from db.events import get_event_users_collection
from models.constants import OutputStatus
from models.common import jsonify


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.projection = {"createdAt": 0, "updatedAt": 0, "_id": 0}
        self.event_users_collection = get_event_users_collection()

    def prepare_query(self) -> dict:
        if self.input.slug:
            query = {"source": self.input.slug}
        else:
            query = {}
        return query

    def fetch_event_users(self, query: dict) -> list:

        if self.input.size and self.input.page:
            offset = int((int(self.input.page) - 1) * int(self.input.size))
            return list(self.event_users_collection.find(
                query, self.projection).skip(offset).limit(int(self.input.size)))

        return list(self.event_users_collection.find(query, self.projection))

    def compute(self) -> Output:
        query = self.prepare_query()
        event_users = self.fetch_event_users(query)

        event_users = [jsonify(event_user) for event_user in event_users]

        return Output(
            output_details=event_users,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched events"
        )
