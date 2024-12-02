from shared.db.events import get_event_users_collection, get_contirbute_event_users_collection
from shared.models.interfaces import GetEventUsersInput as Input, Output
from shared.models.constants import OutputStatus
from pymongo.collection import Collection
from shared.models.common import Common
from typing import Tuple


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.projection = {"_id": 0}
        self.event_users_collection, self.contribute = self.determine_collection()

    def determine_collection(self) -> Tuple[Collection, bool]:
        if self.input.events_type and self.input.events_type.lower() == "contribute":
            return get_contirbute_event_users_collection(), True
        return get_event_users_collection(), False

    def prepare_query(self) -> dict:
        query = {}
        if self.input.slug:
            query = {"source": self.input.slug}
            if self.contribute:
                query = {"slug": self.input.slug}

        filter_query = Common.get_filter_query(
            self.input.filter_field, self.input.filter_value)
        return {**query, **filter_query}

    def fetch_event_users(self, query: dict) -> list:

        if self.input.size and self.input.page:
            offset = int((int(self.input.page) - 1) * int(self.input.size))
            return list(self.event_users_collection.find(
                query, self.projection).skip(offset).limit(int(self.input.size)))

        return list(self.event_users_collection.find(query, self.projection))

    def compute(self) -> Output:
        query = self.prepare_query()
        event_users = self.fetch_event_users(query)

        event_users = [Common.jsonify(event_user)
                       for event_user in event_users]

        total = self.event_users_collection.count_documents(query)

        if len(event_users) == 0:
            return Output(
                output_details=[],
                output_status=OutputStatus.SUCCESS,
                output_message="No event users found"
            )

        return Output(
            output_details={"data": event_users, "total": total},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched event users"
        )
