from db.events import get_events_collection, get_contribute_events_collection
from models.interfaces import GetEventsInput as Input, Output
from models.constants import OutputStatus
from pymongo.collection import Collection
from models.common import Common


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.projection = {"_id": 0, "lastModifiedBy": 0}
        self.events_collection = self.determine_collection()
        self.event_categories = ["support_groups",
                                 "active_together", "wellness_connect"]

    def determine_collection(self) -> Collection:
        if self.input.events_type and self.input.events_type.lower() == "contribute":
            return get_contribute_events_collection()
        return get_events_collection()

    def prepare_query(self) -> dict:
        query = {"$or": [{"isDeleted": False},
                         {"isDeleted": {"$exists": False}}]}
        if self.input.fromToday and self.input.fromToday.lower() == "true":
            currentTime = self.common.current_time
            query["validUpto"] = {"$gte": currentTime}

        filter_query = Common.get_filter_query(
            self.input.filter_field, self.input.filter_value)
        return {**query, **filter_query}

    def fetch_homepage_events(self, query: dict) -> list:
        events = []
        for category in self.event_categories:
            query["category"] = category
            event = list(self.events_collection.find(
                query, self.projection).sort("validUpto", 1).limit(1))
            if len(event) > 0:
                events.append(dict(event[0]))
        if len(events) < 3:
            query.pop("category")
            cursor = self.events_collection.find(
                query, self.projection).sort("validUpto", 1).limit(3 - len(events))
            events.extend(list(cursor))
        return events

    def compute(self) -> Output:
        if self.input.slug is not None:
            query = {"slug": self.input.slug}
            event = dict(self.events_collection.find_one(
                query, self.projection))
            events = [Common.jsonify(event)]
        else:
            query = self.prepare_query()
            if self.input.isHomePage and self.input.isHomePage.lower() == "true":
                events = self.fetch_homepage_events(query)
                events = [Common.jsonify(event) for event in events]
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
