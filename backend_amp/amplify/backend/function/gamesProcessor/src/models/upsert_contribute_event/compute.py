import random
import string
from bson import ObjectId
from shared.models.common import Common
from shared.models.constants import OutputStatus
from shared.db.events import get_contribute_events_collection
from shared.models.interfaces import ContributeEvent as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.events_collection = get_contribute_events_collection()
        self.existing_slugs = self.events_collection.distinct('slug')

    def validate_slug(self, slug: str) -> bool:
        return True if slug in self.existing_slugs else False

    def generate_slug(self) -> str:
        while True:
            slug = ''.join(random.choices(string.ascii_lowercase, k=3))
            if not self.validate_slug(slug):
                return slug

    def prep_data(self, event_data: dict, new_event=True) -> dict:
        date_fields = ["validUpto", "startDate"]
        for field in date_fields:
            event_data[field] = Common.string_to_date(event_data, field)

        if "sub_category" in event_data and isinstance(event_data["sub_category"], str):
            event_data["sub_category"] = ObjectId(event_data["sub_category"])

        if new_event:
            event_data["createdAt"] = self.common.current_time
            event_data["slug"] = self.generate_slug()
        event_data["updatedAt"] = self.common.current_time
        event_data = {k: v for k, v in event_data.items() if v is not None}
        return event_data

    def compute(self) -> Output:
        event_data = self.input.__dict__

        if self.validate_slug(self.input.slug):
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
