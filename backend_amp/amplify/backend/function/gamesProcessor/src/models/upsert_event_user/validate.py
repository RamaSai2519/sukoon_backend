from shared.models.interfaces import EventUserInput as Input
from shared.db.events import get_events_collection


class Validator():
    def __init__(self, input: Input) -> None:
        self.input = input
        self.events_collection = get_events_collection()

    def validate_input(self) -> tuple:
        query = {'slug': self.input.source}
        event = self.events_collection.find_one(query)
        if not event:
            return False, "Invalid source"

        return True, ""
