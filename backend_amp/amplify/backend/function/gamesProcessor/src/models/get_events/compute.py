from shared.db.events import get_events_collection, get_contribute_events_collection, get_event_users_collection, get_contirbute_event_users_collection
from shared.models.interfaces import GetEventsInput as Input, Output
from shared.models.constants import OutputStatus
from pymongo.collection import Collection
from shared.models.common import Common
from datetime import timedelta
from bson import ObjectId


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.projection = {"_id": 0, "lastModifiedBy": 0}
        self.events_collection = self.determine_collection()
        self.event_users_collection = get_event_users_collection()
        self.contirbute_event_users_collection = get_contirbute_event_users_collection()
        self.event_categories = ["support_groups",
                                 "active_together", "wellness_connect"]

    def determine_collection(self) -> Collection:
        if self.input.events_type and self.input.events_type.lower() in ["contribute", "sukoon"]:
            return get_contribute_events_collection()
        return get_events_collection()

    def prepare_query(self) -> dict:
        query = {"$or": [{"isDeleted": False},
                         {"isDeleted": {"$exists": False}}]}
        if self.input.events_type and self.input.events_type.lower() == "sukoon":
            query["isSukoon"] = True
        if self.input.fromToday and self.input.fromToday.lower() == "true":
            currentTime = self.common.current_time - timedelta(hours=2)
            query["validUpto"] = {"$gte": currentTime}

        if self.input.filter_field == "sub_category":
            category_ids = self.input.filter_value.split(",")
            category_ids = [ObjectId(v.strip()) for v in category_ids]
            self.input.filter_value = category_ids
            filter_query = {"sub_category": {"$in": self.input.filter_value}}
        else:
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
            query["slug"] = {"$nin": [event["slug"] for event in events]}
            cursor = self.events_collection.find(
                query, self.projection).sort("validUpto", 1).limit(3 - len(events))
            events.extend(list(cursor))
        return events

    def mark_registered_events(self, events: list) -> list:
        if self.input.events_type and self.input.events_type.lower() == "contribute":
            query = {'user_id': ObjectId(self.input.user_id)}
            collection = self.contirbute_event_users_collection
            slug_field = 'slug'
        else:
            query = {'phoneNumber': self.input.phoneNumber}
            collection = self.event_users_collection
            slug_field = 'source'

        slugs = collection.distinct(slug_field, query)
        for event in events:
            event['isRegistered'] = event['slug'] in slugs
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
                    query, self.projection).sort(self.input.sort_field, int(self.input.sort_order))
                paginated_cursor = Common.paginate_cursor(
                    cursor, int(self.input.page), int(self.input.size))
                events = list(paginated_cursor)
                events = [Common.jsonify(event) for event in events]

        if self.input.phoneNumber or self.input.user_id:
            events = self.mark_registered_events(events)

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
