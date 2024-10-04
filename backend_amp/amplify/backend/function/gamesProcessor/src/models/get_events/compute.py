from models.interfaces import GetEventsInput as Input, Output
from db.events import get_events_collection
from models.constants import OutputStatus
from models.common import Common
from datetime import datetime


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.offset = int(int(input.page) - 1) * int(input.size)
        self.projection = {"_id": 0, "createdAt": 0,
                           "updatedAt": 0, "lastModifiedBy": 0}
        self.events_collection = get_events_collection()
        self.event_categories = ["support_groups",
                                 "active_together", "wellness_connect"]

    def prepare_query(self) -> dict:
        query = {}
        if self.input.fromToday.lower() == "true":
            currentTime = datetime.now()
            query["validUpto"] = {"$gte": currentTime}
        return query

    def fetch_homepage_events(self, query: dict) -> list:
        events = []
        for category in self.event_categories:
            query["category"] = category
            event = list(self.events_collection.find(
                query, self.projection).sort("validUpto", 1).limit(1))
            if len(event) > 0:
                events.append(dict(event[0]))
        return events

    def compute(self) -> Output:
        if self.input.slug is not None:
            query = {"slug": self.input.slug}
            event = dict(self.events_collection.find_one(
                query, self.projection))
            events = [Common.jsonify(event)]
        else:
            query = self.prepare_query()
            if self.input.isHomePage.lower() == "true":
                events = self.fetch_homepage_events(query)
            else:
                cursor = self.events_collection.find(
                    query, self.projection).sort("validUpto", 1)
                paginated_cursor = Common.paginate_cursor(
                    cursor, int(self.input.page), int(self.input.size))
                events = list(paginated_cursor)
                events = [Common.jsonify(event) for event in events]

        total_events = self.events_collection.count_documents(query)

        if len(events) == 0:
            return Output(
                output_details=[],
                output_status=OutputStatus.FAILURE,
                output_message="No events found"
            )

        return Output(
            output_details={"data": events, "total": total_events},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched events"
        )
