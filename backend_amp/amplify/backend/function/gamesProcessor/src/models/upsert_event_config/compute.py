import dataclasses
from bson import ObjectId
from shared.models.common import Common
from shared.models.constants import OutputStatus
from shared.db.events import get_events_collection
from shared.models.interfaces import Event as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.events_collection = get_events_collection()

    def prep_data(self, event_data: dict, new_event=True):
        date_fields = ["validUpto",
                       "registrationAllowedTill", "startEventDate"]
        for field in date_fields:
            event_data[field] = Common.string_to_date(event_data, field)

        if new_event:
            event_data["createdAt"] = self.common.current_time
        event_data["updatedAt"] = self.common.current_time

        if self.input.isDeleted == True:
            event_data["deletedBy"] = ObjectId(self.common.get_identity())

        event_data = {k: v for k, v in event_data.items() if v is not None}
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
            output_details=Common.jsonify(event_data),
            output_status=OutputStatus.SUCCESS,
            output_message=message
        )
