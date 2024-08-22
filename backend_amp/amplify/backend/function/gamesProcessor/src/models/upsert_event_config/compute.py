import dataclasses
from datetime import datetime
from models.constants import OutputStatus
from db.events import get_events_collection
from models.interfaces import EventInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.events_collection = get_events_collection()

    def prep_data(self, event_data, new_event=True):
        event_data["validUpto"] = datetime.strptime(
            event_data["validUpto"], "%Y-%m-%dT%H:%M:%S.%fZ")

        if "registrationAllowedTill" in event_data:
            event_data["registrationAllowedTill"] = datetime.strptime(
                event_data["registrationAllowedTill"], "%Y-%m-%dT%H:%M:%S.%fZ")

        if "startEventDate" in event_data:
            event_data["startEventDate"] = datetime.strptime(
                event_data["startEventDate"], "%Y-%m-%dT%H:%M:%S.%fZ")

        if new_event:
            event_data["createdAt"] = datetime.now()
        event_data["updatedAt"] = datetime.now()

        return event_data

    def __format__(self, format_spec: dict) -> dict:
        if "registrationAllowedTill" in format_spec:
            format_spec["registrationAllowedTill"] = datetime.strftime(
                format_spec["registrationAllowedTill"], "%Y-%m-%dT%H:%M:%S")

        if "startEventDate" in format_spec:
            format_spec["startEventDate"] = datetime.strftime(
                format_spec["startEventDate"], "%Y-%m-%dT%H:%M:%S")

        if "validUpto" in format_spec:
            format_spec["validUpto"] = datetime.strftime(
                format_spec["validUpto"], "%Y-%m-%dT%H:%M:%S")

        format_spec.pop("createdAt", None)
        format_spec.pop("updatedAt", None)

        return format_spec

    def validate_slug(self, slug: str) -> bool:
        event = self.events_collection.find_one({"slug": slug})
        return True if event else False

    def compute(self) -> Output:
        event_data = self.input
        event_data = dataclasses.asdict(event_data)
        event_data.pop('action', None)
        event_data.pop('id', None)

        if self.validate_slug(event_data["slug"]):
            event_data = self.prep_data(event_data, new_event=False)
            self.events_collection.update_one(
                {"slug": event_data["slug"]},
                {"$set": event_data}
            )
        else:
            event_data = self.prep_data(event_data)
            self.events_collection.insert_one(event_data)

        event_data = self.__format__(event_data)

        return Output(
            output_details=event_data,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully created event"
        )
