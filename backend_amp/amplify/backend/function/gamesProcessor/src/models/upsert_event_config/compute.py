import dataclasses
from datetime import datetime
from models.constants import OutputStatus
from db.events import get_events_collection
from models.interfaces import EventInput as Input, Output
from models.common import string_to_date, jsonify


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.events_collection = get_events_collection()

    def prep_data(self, event_data, new_event=True):
        date_fields = ["validUpto",
                       "registrationAllowedTill", "startEventDate"]
        for date_field in date_fields:
            event_data[date_field] = string_to_date(event_data, date_field)

        if new_event:
            event_data["createdAt"] = datetime.now()
        event_data["updatedAt"] = datetime.now()

        return event_data

    def validate_slug(self, slug: str) -> bool:
        event = self.events_collection.find_one({"slug": slug})
        return True if event else False

    def compute(self) -> Output:
        event_data = self.input
        event_data = dataclasses.asdict(event_data)

        if self.validate_slug(event_data["slug"]):
            event_data = self.prep_data(event_data, new_event=False)
            self.events_collection.update_one(
                {"slug": event_data["slug"]},
                {"$set": event_data}
            )
            message = "Successfully updated event"
        else:
            event_data = self.prep_data(event_data)
            self.events_collection.insert_one(event_data)
            message = "Successfully created event"

        return Output(
            output_details=jsonify(event_data),
            output_status=OutputStatus.SUCCESS,
            output_message=message
        )
