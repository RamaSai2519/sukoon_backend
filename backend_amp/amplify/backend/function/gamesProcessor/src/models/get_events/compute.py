from models.interfaces import getEventsInput as Input, Output
from db.events import get_events_collection
from models.constants import OutputStatus
from datetime import datetime


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.offset = int(int(input.page) - 1) * int(input.limit)
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
        events_collection = get_events_collection()
        for category in self.event_categories:
            query["category"] = category
            event = list(events_collection.find(
                query, self.projection).sort("validUpto", 1).limit(1))
            if len(event) > 0:
                events.append(dict(event[0]))
        return events

    def __format__(self, events: list) -> list:
        for event in events:
            if "registrationAllowedTill" in event:
                event["registrationAllowedTill"] = datetime.strftime(
                    event["registrationAllowedTill"], "%Y-%m-%dT%H:%M:%S")
            if "startEventDate" in event:
                event["startEventDate"] = datetime.strftime(
                    event["startEventDate"], "%Y-%m-%dT%H:%M:%S")
            if "validUpto" in event:
                event["validUpto"] = datetime.strftime(
                    event["validUpto"], "%Y-%m-%dT%H:%M:%S")

        return events

    def compute(self) -> Output:
        events_collection = get_events_collection()
        query = self.prepare_query()
        if self.input.isHomePage.lower() == "true":
            events = self.fetch_homepage_events(query)
        else:
            events = list(events_collection.find(
                query, self.projection).sort("validUpto", 1).skip(self.offset).limit(int(self.input.limit)))

        events = self.__format__(events)
        print(len(events))

        return Output(
            output_details=events,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched events"
        )
