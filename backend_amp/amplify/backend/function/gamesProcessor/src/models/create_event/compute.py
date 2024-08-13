import dataclasses
from models.constants import OutputStatus
from db_queries.mutations.event import create_event
from models.interfaces import EventInput as Input, Output

class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input

    def compute(self) -> Output:
        event_data = self.input
        event_data = dataclasses.asdict(event_data)
        event_data.pop('action', None)
        event_data.pop('id', None)

        response = create_event(event_data)

        return Output(
            output_details=response,
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully created event"
       )